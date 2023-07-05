from braket.circuits.circuit_helpers import validate_circuit_and_shots
from qiskit.circuit import Measure
from qiskit.transpiler import Target, InstructionProperties
from qiskit_braket_provider.exception import QiskitBraketException


import datetime
from abc import ABC
from typing import Union, List, Optional, Tuple, Dict

from qiskit.providers import BackendV2, Provider, Options
from qiskit_braket_provider.providers.adapter import wrap_circuits_in_verbatim_box


from qiskit.circuit import Instruction as QiskitInstruction
from .client.backend_dtos import ConfigurationDto, TYPE, BackendDto, ConnectivityDto
from .client.client_dtos import JobDto, INPUT_FORMAT
from .job import PlanqkJob
from planqk.qiskit.providers.helper.adapter import _op_to_instruction, convert_qiskit_to_planqk_circuit, transform_to_qasm_3_program
from .providers.helper.job_input_converter import convert_circuit_to_backend_input

TASK_ID_DIVIDER = ";"


# class PlanqkBackend(BackendV2, ABC):
#     """BraketBackend."""
#
#     def __repr__(self):
#         return f"PlanqkBraketBackend[{self.name}]"


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
            >>> provider = PlanqkProvider()
            >>> backend = provider.get_backend("SV1")
            >>> transpiled_circuit = transpile(input, backend=backend)
            >>> backend.run(transpiled_circuit, shots=10).result().get_counts()
            {"100": 10, "001": 10}

        Args:
            backend_info: PlanQK backend infos
            provider: Qiskit provider for this backend
            name: name of backend
            description: description of backend
            online_date: online date
            backend_version: backend version
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

    def _planqk_backend_to_target(self) -> Target:
        """Converts properties of a PlanQK backend into Qiskit Target object.

        Args:
            planqk_backend: PlanQK backend

        Returns:
            target for Qiskit backend
        """
        # building target
        target = Target(description=f"Target for PlanQK backend {self.name}")

        configuration: ConfigurationDto = self._backend_info.configuration
        qubit_count: int = configuration.qubit_count
        # gate model devices
        if self._backend_info.type == TYPE.QPU:

            connectivity: ConnectivityDto = self._backend_info.configuration.connectivity
            instructions: List[QiskitInstruction] = []

            for operation in configuration.gates:
                instruction = _op_to_instruction(operation.name) #TODO cchek if finction impl
                if instruction is not None:
                    # TODO: remove when target will be supporting > 2 qubit gates  # pylint:disable=fixme
                    if instruction.num_qubits <= 2:
                        instructions.append(instruction)

            # add measurement instructions
            target.add_instruction(
                Measure(), {(i,): None for i in range(qubit_count)}
            )

            for instruction in instructions:
                instruction_props: Optional[
                    Dict[
                        Union[Tuple[int], Tuple[int, int]], Optional[InstructionProperties]
                    ]
                ] = {}
                # adding 1 qubit instructions
                if instruction.num_qubits == 1:
                    for i in range(qubit_count):
                        instruction_props[(i,)] = None
                # adding 2 qubit instructions
                elif instruction.num_qubits == 2:
                    # building coupling map for fully connected device
                    if connectivity.fully_connected:
                        for src in range(qubit_count):
                            for dst in range(qubit_count):
                                if src != dst:
                                    instruction_props[(src, dst)] = None
                                    instruction_props[(dst, src)] = None
                    # building coupling map for device with connectivity graph
                    else:
                        for src, connections in connectivity.graph.items():
                            for dst in connections:
                                instruction_props[(int(src), int(dst))] = None
                # for more than 2 qubits
                else:
                    instruction_props = None
                # TODO other architcture not inoq
                target.add_instruction(instruction, instruction_props)

        # gate model simulators
        elif self._backend_info.type == TYPE.SIMULATOR:
            instructions = []

            for operation in configuration.gates:
                instruction = _op_to_instruction(operation.name)
                if instruction is not None:
                    # TODO: remove when target will be supporting > 2 qubit gates  # pylint:disable=fixme
                    if instruction.num_qubits <= 2:
                        instructions.append(instruction)

            # add measurement instructions
            target.add_instruction(
                Measure(), {(i,): None for i in range(qubit_count)}
            )

            for instruction in instructions:
                simulator_instruction_props: Optional[
                    Dict[
                        Union[Tuple[int], Tuple[int, int]],
                        Optional[InstructionProperties],
                    ]
                ] = {}
                # adding 1 qubit instructions
                if instruction.num_qubits == 1:
                    for i in range(qubit_count):
                        simulator_instruction_props[(i,)] = None
                # adding 2 qubit instructions
                elif instruction.num_qubits == 2:
                    # building coupling map for fully connected device
                    for src in range(qubit_count):
                        for dst in range(qubit_count):
                            if src != dst:
                                simulator_instruction_props[(src, dst)] = None
                                simulator_instruction_props[(dst, src)] = None
                target.add_instruction(instruction, simulator_instruction_props)

        else:
            raise QiskitBraketException(
                "Cannot create target from PlanQK backend information."
            )

        return target

    @property
    def target(self):
        return self._target

    @property
    def max_circuits(self):
        return None

    @classmethod
    def _default_options(cls):
        return Options()

    def run(self, circuit, **kwargs):
        if isinstance(circuit, (list, tuple)):
            if len(circuit) > 1:
                raise RuntimeError("Multi-experiment jobs are not supported")
            circuit = circuit[0]

        shots = kwargs.get('shots', 1)  # TODO externalize - use backen min default

        # TODO input params

        input = convert_circuit_to_backend_input(self._backend_info.configuration.supported_input_formats, circuit)

        # import qiskit.qasm3 as q3  TODO try in verbatim box
        # qasm_circuit_ibm = q3.dumps(input)
        # qasm_circuit_ibm = qasm_circuit_ibm.replace('\ninclude "stdgates.inc";', '')
        #TODO this is braket backend specific -> move
        input_params = {'disable_qubit_rewiring': False,
                        'qubit_count': circuit.num_qubits}  # TODO determine QuBit count in backend

        job_request = JobDto(self._backend_info.id,
                             provider=self._backend_info.provider.name,
                             input_format=input[0],
                             input=input[1],
                             shots=shots,
                             input_params=input_params)

        return PlanqkJob(backend=self, job_details=job_request)

    def retrieve_job(self, job_id: str) -> PlanqkJob:
        """Return a single job submitted to the backend.

        Args:
            job_id: ID of the job to retrieve.

        Returns:
            The job with the given ID.
        """

        return PlanqkJob(backend=self, job_id=job_id)