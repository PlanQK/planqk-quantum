"""AWS Braket backends."""

import datetime
import logging
from abc import ABC
from typing import Iterable, Union, List

from braket.circuits.circuit_helpers import validate_circuit_and_shots
from qiskit import QuantumCircuit
from qiskit.providers import BackendV2, QubitProperties, Options, Provider
from qiskit_braket_provider.providers.adapter import wrap_circuits_in_verbatim_box

from planqk.qiskit.providers.helper.adapter import (
    aws_device_to_target, convert_qiskit_to_planqk_circuit, transform_to_qasm_3_program,
)
from ...client.client_dtos import BackendDto, JobDto, INPUT_FORMAT
from ...job import PlanqkJob

logger = logging.getLogger(__name__)

TASK_ID_DIVIDER = ";"


class BraketBackend(BackendV2, ABC):
    """BraketBackend."""

    def __repr__(self):
        return f"PlanqkBraketBackend[{self.name}]"


class PlanqkAWSBraketBackend(BraketBackend):
    """_PlanqkAWSBraketBackend."""

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
        """_PlanqkAWSBraketBackend for execution circuits against AWS Braket devices.

        Example:
            >>> provider = AWSBraketProvider()
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
        self._target = aws_device_to_target(backend_info=backend_info)

    def retrieve_job(self, job_id: str) -> PlanqkJob:
        """Return a single job submitted to AWS backend.

        Args:
            job_id: ID of the job to retrieve.

        Returns:
            The job with the given ID.
        """

        return PlanqkJob(backend=self, job_id=job_id)

    @property
    def target(self):
        return self._target

    @property
    def max_circuits(self):
        return None

    @classmethod
    def _default_options(cls):
        return Options()

    def qubit_properties(
            self, qubit: Union[int, List[int]]
    ) -> Union[QubitProperties, List[QubitProperties]]:
        # TODO: fetch information from device.properties.provider  # pylint: disable=fixme
        raise NotImplementedError

    @property
    def dtm(self) -> float:
        raise NotImplementedError(
            f"System time resolution of output signals is not supported by {self.name}."
        )

    @property
    def meas_map(self) -> List[List[int]]:
        raise NotImplementedError(f"Measurement map is not supported by {self.name}.")

    def drive_channel(self, qubit: int):
        raise NotImplementedError(f"Drive channel is not supported by {self.name}.")

    def measure_channel(self, qubit: int):
        raise NotImplementedError(f"Measure channel is not supported by {self.name}.")

    def acquire_channel(self, qubit: int):
        raise NotImplementedError(f"Acquire channel is not supported by {self.name}.")

    def control_channel(self, qubits: Iterable[int]):
        raise NotImplementedError(f"Control channel is not supported by {self.name}.")

    def run(self, circuit: QuantumCircuit, **kwargs) -> PlanqkJob:

        if isinstance(circuit, (list, tuple)):
            if len(circuit) > 1:
                raise RuntimeError("Multi-experiment jobs are not supported")
            circuit = circuit[0]

        shots = kwargs.get('shots', 1)  # TODO externalize

        braket_circuit = convert_qiskit_to_planqk_circuit(circuit)
        validate_circuit_and_shots(braket_circuit, shots)

        if kwargs.pop("verbatim", False):
            braket_circuit = wrap_circuits_in_verbatim_box(braket_circuit)

        # TODO multiple circuits
        # TODO input params

        qasm_circuit = transform_to_qasm_3_program(braket_circuit, False, {})

        # import qiskit.qasm3 as q3  TODO try in verbatim box
        # qasm_circuit_ibm = q3.dumps(input)
        # qasm_circuit_ibm = qasm_circuit_ibm.replace('\ninclude "stdgates.inc";', '')
        input_params = {'disableQubitRewiring': False, 'qubit_count': braket_circuit.qubit_count}  # TODO determine QuBit count

        job_request = JobDto(self._backend_info.id,
                             provider=self._backend_info.provider,  # TODO remove - can be decided in backend
                             input=qasm_circuit,
                             circuit_type=INPUT_FORMAT.OPEN_QASM_V3,
                             shots=shots,
                             input_params=input_params)

        return PlanqkJob(backend=self, job_details=job_request)
