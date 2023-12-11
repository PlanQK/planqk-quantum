import datetime
from abc import ABC

from qiskit.circuit import Delay, Parameter
from qiskit.circuit import Measure
from qiskit.providers import BackendV2, Provider, Options
from qiskit.providers.models import QasmBackendConfiguration, GateConfig
from qiskit.transpiler import Target

from planqk.qiskit.providers.job_input_converter import convert_circuit_to_backend_input
from .client.backend_dtos import ConfigurationDto, TYPE, BackendDto, ConnectivityDto, PROVIDER, HARDWARE_PROVIDER
from .client.job_dtos import JobDto
from .job import PlanqkJob
from .providers.adapter import ProviderAdapterFactory


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
        super().__init__(
            provider=provider,
            name=name,
            description=description,
            online_date=online_date,
            backend_version=backend_version,
            **fields,
        )
        self._backend_info = backend_info
        self._target = self._planqk_backend_to_target()
        self._configuration = self._planqk_backend_dto_to_configuration()

    def _planqk_backend_to_target(self) -> Target:
        """Converts properties of a PlanQK actual into Qiskit Target object.

        Returns:
            target for Qiskit actual
        """
        # building target
        configuration: ConfigurationDto = self._backend_info.configuration
        qubit_count: int = configuration.qubit_count
        target = Target(description=f"Target for PlanQK actual {self.name}", num_qubits=qubit_count)

        is_simulator = self._backend_info.type == TYPE.SIMULATOR
        qubits = configuration.qubits
        connectivity: ConnectivityDto = self._backend_info.configuration.connectivity

        adapter = ProviderAdapterFactory.get_adapter(self._backend_info.provider)

        single_qubit_props = adapter.single_qubit_gate_props(qubits, is_simulator)
        multi_qubit_props = adapter.multi_qubit_gate_props(qubits, connectivity, is_simulator)
        for gate in configuration.gates:
            name = gate.name
            gate = adapter.op_to_instruction(name)

            if gate is None:
                continue

            if gate.num_qubits == 1:
                target.add_instruction(gate, single_qubit_props)
            elif gate.num_qubits == 2:
                target.add_instruction(gate, multi_qubit_props)
            elif gate.num_qubits == 0 and single_qubit_props == {None: None}:
                # For gates without qubit number qargs can not be determined
                target.add_instruction(gate, {None: None})

        target.add_instruction(Measure(), single_qubit_props)

        if "delay" in configuration.instructions and "delay" not in target:
            # gate_props = {None: None} if is_simulator else single_qubit_gate_props()
            target.add_instruction(Delay(Parameter("t")), single_qubit_props)

        return target

    def _planqk_backend_dto_to_configuration(self) -> QasmBackendConfiguration:
        basis_gates = [self._get_gate_config_from_target(basis_gate.name)
                       for basis_gate in self._backend_info.configuration.gates if basis_gate.native_gate
                       and self._get_gate_config_from_target(basis_gate.name) is not None]
        gates = [self._get_gate_config_from_target(gate.name)
                 for gate in self._backend_info.configuration.gates if not gate.native_gate
                 and self._get_gate_config_from_target(gate.name) is not None]

        return QasmBackendConfiguration(
            backend_name=self.name,
            backend_version=self.backend_version,
            n_qubits=self._backend_info.configuration.qubit_count,
            basis_gates=basis_gates,
            gates=gates,
            local=False,
            simulator=self._backend_info.type == TYPE.SIMULATOR,
            conditional=False,
            open_pulse=False,
            memory=self._backend_info.configuration.memory_result_supported,
            max_shots=self._backend_info.configuration.shots_range.max,
            coupling_map=self.coupling_map,
            supported_instructions=self._target.instructions,
            max_experiments=self._backend_info.configuration.shots_range.max,  # Only one circuit is supported per job
            description=self._backend_info.documentation.description,
            min_shots=self._backend_info.configuration.shots_range.min,
        )

    def _get_gate_config_from_target(self, name) -> GateConfig:
        operations = [operation for operation in self._target.operations
                      if operation.name.casefold() == name.casefold()]
        if len(operations) == 1:
            operation = operations[0]
            return GateConfig(
                name=name,
                parameters=operation.params,
                qasm_def='')

    @property
    def target(self):
        return self._target

    @property
    def max_circuits(self):
        return None

    @property
    def min_shots(self):
        return self._backend_info.configuration.shots_range.min

    @property
    def max_shots(self):
        return self._backend_info.configuration.shots_range.max

    @classmethod
    def _default_options(cls):
        return Options(shots=1024)

    def run(self, circuit, **kwargs) -> PlanqkJob:
        """Run a circuit on the backend as job.
            Args:
                circuit (QuantumCircuit): circuit to run. Currently only a single circuit can be executed per job.
                **kwargs: additional arguments for the execution (see below)
            Returns:
                PlanqkJob: The job instance for the circuit that was run.
        """
        self._validate_provider_for_backend()

        if isinstance(circuit, (list, tuple)):
            if len(circuit) > 1:
                raise ValueError("Multi-experiment jobs are not supported")
            circuit = circuit[0]

        # PennyLane-Qiskit Plugin identifies the result based on the circuit name which must be "circ0"
        circuit.name = "circ0"
        shots = kwargs.get('shots', self._backend_info.configuration.shots_range.min)

        # TODO add support for input params

        input_circ = convert_circuit_to_backend_input(self._backend_info.configuration.supported_input_formats, circuit)

        # TODO this is braket specific
        input_params = {'disable_qubit_rewiring': False,
                        'qubit_count': circuit.num_qubits}

        job_request = JobDto(backend_id=self._backend_info.id,
                             provider=self._backend_info.provider.name,
                             input_format=input_circ[0],
                             input=input_circ[1],
                             shots=shots,
                             input_params=input_params)

        return PlanqkJob(backend=self, job_details=job_request)

    def _validate_provider_for_backend(self) -> bool:
        from planqk.qiskit.runtime_provider import PlanqkQiskitRuntimeService
        if (self._backend_info.hardware_provider == HARDWARE_PROVIDER.IBM
                and not isinstance(self.provider, PlanqkQiskitRuntimeService)):
            raise ValueError(f"Jobs for IBM backends must not be created with {self.provider.__class__.__name__}. "
                             f"Use {PlanqkQiskitRuntimeService.__name__} instead.")

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
        return self._backend_info.provider
