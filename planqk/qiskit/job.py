import copy
import logging

from qiskit.providers import JobV1 as Job, JobStatus, BackendV1 as Backend
from qiskit.result import Result

from planqk.client import PlanqkClient
from planqk.exceptions import PlanqkError

logger = logging.getLogger(__name__)


class JobDetails:
    def __init__(self, backend_name, status=JobStatus.INITIALIZING, **kwargs):
        self._data = {}
        self.backend_name = backend_name
        self.status = status
        self._data.update(kwargs)

    @classmethod
    def from_dict(cls, data):
        in_data = copy.copy(data)
        status = JobStatus(in_data.pop('job_status'))
        in_data['status'] = status
        return cls(**in_data)


class PlanqkQuantumJob(Job):
    def __init__(self, client: PlanqkClient, backend: Backend, **kwargs) -> None:
        self._client = client
        self._backend = backend
        self._details = JobDetails(backend_name=backend.name())
        self.metadata = kwargs
        super().__init__(backend, self.submit(), **kwargs)

    def submit(self):
        """
        Submits the job for execution
        """
        circuit_qasm = self.metadata.pop('circuit_qasm', None),
        if circuit_qasm is None:
            raise PlanqkError('Attribute "circuit_qasm" must not be None')
        payload = {
            'backend_name': self._backend.name(),
            'circuit_qasm': circuit_qasm[0],  # for some reason 'circuit_qasm' is a tuple
            'job_configuration': self.metadata,
        }
        job = self._client.submit_job(payload)
        job_id = job.get('id', None)
        if job_id is None:
            raise PlanqkError('Error submitting job: attribute "job_id" must not be None')
        return job_id

    def status(self):
        """
        Refreshes the job metadata and returns the status of the job, among the values of ``JobStatus``.
        """
        job = self._client.get_job(self.job_id())
        self._details = JobDetails.from_dict(job)
        return self._details.status

    def cancel(self):
        """
        Attempt to cancel the job; currently not supported
        """
        return

    def result(self, timeout=None):
        """
        Return the results of the job
        """
        self.wait_for_final_state(timeout=timeout)
        result = self._client.get_job_result(self.job_id())
        return Result.from_dict(result)
