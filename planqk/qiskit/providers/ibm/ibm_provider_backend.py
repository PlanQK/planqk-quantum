import json
from typing import Dict
from typing import Optional, List

from qiskit import QuantumCircuit
from qiskit.providers.models import BackendStatus
from qiskit_ibm_provider import IBMBackend
from qiskit_ibm_provider.job import IBMCircuitJob
from qiskit_ibm_provider.utils import RuntimeEncoder

from planqk.qiskit import PlanqkJob
from planqk.qiskit.client.backend_dtos import STATUS
from planqk.qiskit.client.client import _PlanqkClient
from planqk.qiskit.client.job_dtos import JobDto, INPUT_FORMAT, RuntimeJobParamsDto
from planqk.qiskit.planqk_runtime_job import PlanqkRuntimeJob
from planqk.qiskit.providers.ibm.ibm_backend import PlanqkIbmBackend


def _encode_circuit_base64(circuit: QuantumCircuit):
    # Transforms circuit to base64 encoded byte stream
    input_json_str = json.dumps(circuit, cls=RuntimeEncoder)
    # Transform back to json but with the base64 encoded byte stream
    return json.loads(input_json_str)


class PlanqkIbmProviderBackend(PlanqkIbmBackend):

    def __init__(self, **kwargs):
        PlanqkIbmBackend.__init__(self, **kwargs)
        self.ibm_backend = IBMBackend(configuration=self.configuration(), provider=None, api_client=None)
        self.ibm_backend._runtime_run = self._submit_job
        self.ibm_backend.status = self.status

    def run(self, circuit, **kwargs) -> PlanqkRuntimeJob:
        return IBMBackend.run(self.ibm_backend, circuit, **kwargs)

    def status(self):
        operational = self.backend_info.status == STATUS.ONLINE
        status_msg = "active" if operational else self.backend_info.status.name.lower()
        pending_jobs = 0  # TODO set pending jobs

        return BackendStatus.from_dict({'backend_name': self.name,
                                        'backend_version': self.backend_version,
                                        'operational': operational,
                                        'status_msg': status_msg,
                                        'pending_jobs': pending_jobs})

    def _submit_job(
            self,
            program_id: str,
            inputs: Dict,
            backend_name: str,
            job_tags: Optional[List[str]] = None,
            image: Optional[str] = None,
    ) -> IBMCircuitJob:
        encoded_input = _encode_circuit_base64(circuit=inputs)
        hgp_name = 'ibm-q/open/main'

        runtime_job_params = RuntimeJobParamsDto(
            program_id=program_id,
            hgp=hgp_name
        )

        job_request = JobDto(backend_id=self.backend_info.id,
                             provider=self.backend_info.provider.name,
                             input_format=INPUT_FORMAT.QISKIT,
                             input=encoded_input,
                             shots=inputs.get('shots'),
                             input_params=runtime_job_params.dict())

        return PlanqkRuntimeJob(backend=self, job_details=job_request)

    def retrieve_job(self, job_id: str) -> PlanqkJob:
        job_details = _PlanqkClient.get_job(job_id)
        return PlanqkRuntimeJob(backend=self, job_id=job_id, job_details=job_details)
