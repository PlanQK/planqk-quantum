import datetime
from abc import ABC, abstractmethod
from copy import copy
from typing import Optional, Tuple

from qiskit import QuantumCircuit
from qiskit.circuit import Instruction as QiskitInstruction, Delay, Parameter
from qiskit.circuit import Measure
from qiskit.providers import BackendV2, Provider
from qiskit.providers.models import QasmBackendConfiguration, GateConfig
from qiskit.transpiler import Target

from .client.backend_dtos import ConfigurationDto, TYPE, BackendDto, PROVIDER
from .client.job_dtos import JobDto, INPUT_FORMAT
from .job import PlanqkJob
from .options import OptionsV2


class PlanqkBackend(BackendV2, ABC):

    def __init__(  # pylint: disable=too-many-arguments
            self,
            backend_info: BackendDto,
            provider: Provider = None,
            name: str = None,
            description: str = None,
            online_date: datetime.datetime = None,
            backend_version: str = None,
            **fields,
    ):
        """PlanqkBackend for execution circuits against PlanQK devices.

        Example:
            provider = PlanqkProvider()
            actual = provider.get_backend("azure.ionq.simulator")
            transpiled_circuit = transpile(input, actual=actual)
            actual.run(transpiled_circuit, shots=10).result().get_counts()
            {"100": 10, "001": 10}

        Args:
            backend_info: PlanQK actual infos
            provider: Qiskit provider for this actual
            name: name of actual
            description: description of actual
            online_date: online date
            backend_version: actual version
            **fields: other arguments
        """

        BackendV2.__init__(self,
                           provider=provider,
                           name=name,
                           description=description,
                           online_date=online_date,
                           backend_version=backend_version,
                           **fields,
                           )
        self._backend_info = backend_info
        self._is_simulator = self.backend_info.type == TYPE.SIMULATOR
        self._target = self._planqk_backend_to_target()
        self._configuration = self._planqk_backend_dto_to_configuration()
        self._instance = None

    @property
    def backend_info(self):
        return self._backend_info

    @property
    def is_simulator(self):
        return self._is_simulator

    @abstractmethod
    def to_gate(self, name: str):
        pass

    @abstractmethod
    def get_single_qubit_gate_properties(self):
        pass

    @abstractmethod
    def get_multi_qubit_gate_properties(self):
        pass

    non_gate_instr_mapping = {
        "delay": Delay(Parameter("t")),
        "measure": Measure(),
    }

    def to_non_gate_instruction(self, name: str) -> Optional[QiskitInstruction]:
        instr = self.non_gate_instr_mapping.get(name, None)
        if instr is not None:
            instr.has_single_gate_props = True
            return instr
        return None

    def _planqk_backend_to_target(self) -> Target:
        """Converts properties of a PlanQK actual into Qiskit Target object.

        Returns:
            target for Qiskit actual
        """
        # building target

        configuration: ConfigurationDto = self.backend_info.configuration
        qubit_count: int = configuration.qubit_count
        target = Target(description=f"Target for PlanQK actual {self.name}", num_qubits=qubit_count)

        single_qubit_props = self.get_single_qubit_gate_properties()
        multi_qubit_props = self.get_multi_qubit_gate_properties()
        gates_names = {gate.name.lower() for gate in configuration.gates}

        for gate in gates_names:
            gate = self.to_gate(gate)

            if gate is None:
                continue

            if gate.num_qubits == 1:
                target.add_instruction(instruction=gate, properties=single_qubit_props)
            elif gate.num_qubits > 1:
                target.add_instruction(instruction=gate, properties=multi_qubit_props)
            elif gate.num_qubits == 0 and single_qubit_props == {None: None}:
                # For gates without qubit number qargs can not be determined
                target.add_instruction(instruction=gate, properties={None: None})

        target.add_instruction(Measure(), single_qubit_props)

        non_gate_instructions = set(configuration.instructions).difference(gates_names).difference({'measure'})
        for non_gate_instruction_name in non_gate_instructions:
            instruction = self.to_non_gate_instruction(non_gate_instruction_name)
            if instruction is not None:
                if instruction.has_single_gate_props:
                    target.add_instruction(instruction, single_qubit_props)
                else:
                    target.add_instruction(instruction=instruction, name=non_gate_instruction_name)

        return target

    def _planqk_backend_dto_to_configuration(self) -> QasmBackendConfiguration:
        basis_gates = [self._get_gate_config_from_target(basis_gate.name)
                       for basis_gate in self.backend_info.configuration.gates if basis_gate.native_gate
                       and self._get_gate_config_from_target(basis_gate.name) is not None]
        gates = [self._get_gate_config_from_target(gate.name)
                 for gate in self.backend_info.configuration.gates if not gate.native_gate
                 and self._get_gate_config_from_target(gate.name) is not None]

        return QasmBackendConfiguration(
            backend_name=self.name,
            backend_version=self.backend_version,
            n_qubits=self.backend_info.configuration.qubit_count,
            basis_gates=basis_gates,
            gates=gates,
            local=False,
            simulator=self.backend_info.type == TYPE.SIMULATOR,
            conditional=False,
            open_pulse=False,
            memory=self.backend_info.configuration.memory_result_supported,
            max_shots=self.backend_info.configuration.shots_range.max,
            coupling_map=self.coupling_map,
            supported_instructions=self._target.instructions,
            max_experiments=self.backend_info.configuration.shots_range.max,  # Only one circuit is supported per job
            description=self.backend_info.documentation.description,
            min_shots=self.backend_info.configuration.shots_range.min,
            online_date=self.backend_info.updated_at  # TODO replace with online date
        )

    def _get_gate_config_from_target(self, name) -> GateConfig:
        operations = [operation for operation in self._target.operations
                      if isinstance(operation.name, str)  # Filters out the IBM conditional instructions having no name
                      and operation.name.casefold() == name.casefold()]
        if len(operations) == 1:
            operation = operations[0]
            return GateConfig(
                name=name,
                parameters=operation.params,
                qasm_def='',
            )

    @property
    def target(self):
        return self._target

    @property
    def max_circuits(self):
        return None

    @property
    def min_shots(self):
        return self.backend_info.configuration.shots_range.min

    @property
    def max_shots(self):
        return self.backend_info.configuration.shots_range.max

    @classmethod
    def _default_options(cls):
        return OptionsV2()

    @abstractmethod
    def convert_to_job_input(self, circuit: QuantumCircuit, options=None) -> Tuple[INPUT_FORMAT, dict]:
        pass

    def convert_to_job_params(self, circuit: QuantumCircuit = None, options=None) -> dict:
        return {}

    @abstractmethod
    def get_job_input_format(self) -> INPUT_FORMAT:
        pass

    def run(self, circuit, **kwargs) -> PlanqkJob:
        """Run a circuit on the backend as job.

        Args:
            circuit (QuantumCircuit): circuit to run. Currently only a single circuit can be executed per job.
            **kwargs: additional arguments for the execution (see below)
        Returns:
            PlanqkJob: The job instance for the circuit that was run.
        """

        if isinstance(circuit, (list, tuple)):
            if len(circuit) > 1:
                raise ValueError("Multi-experiment jobs are not supported")
            circuit = circuit[0]

        # PennyLane-Qiskit Plugin identifies the result based on the circuit name which must be "circ0"
        circuit.name = "circ0"
        shots = kwargs.get('shots', self.backend_info.configuration.shots_range.min)

        # add kwargs, if defined as options, to a copy of the options
        options = copy(self.options)
        if kwargs:
            for field in kwargs:
                if field in options.data:
                    options[field] = kwargs[field]

        job_input_format = self.get_job_input_format()
        job_input = self.convert_to_job_input(circuit, options)
        input_params = self.convert_to_job_params(circuit, options)

        job_request = JobDto(backend_id=self.backend_info.id,
                             provider=self.backend_info.provider.name,
                             input_format=job_input_format,
                             input=job_input,
                             shots=shots,
                             input_params=input_params)

        return PlanqkJob(backend=self, job_details=job_request)

    def retrieve_job(self, job_id: str) -> PlanqkJob:
        """Return a single job.

        Args:
            job_id: id of the job to retrieve.

        Returns:
            The job with the given id.
        """
        return PlanqkJob(backend=self, job_id=job_id)

    def configuration(self) -> QasmBackendConfiguration:
        """Return the actual configuration.

        Returns:
            QasmBackendConfiguration: the configuration for the actual.
        """
        return self._configuration

    @property
    def backend_provider(self) -> PROVIDER:
        """Return the provider offering the quantum backend resource."""
        return self.backend_info.provider
