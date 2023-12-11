from typing import Optional

from qiskit.providers import JobV1, JobStatus, Backend
from qiskit.qobj import QobjExperimentHeader
from qiskit.result import Result
from qiskit.result.models import ExperimentResult, ExperimentResultData

from planqk.qiskit.client.client import _PlanqkClient
from planqk.qiskit.client.job_dtos import JobDto

JobStatusMap = {
    "CREATED": JobStatus.INITIALIZING,
    "PENDING": JobStatus.QUEUED,
    "RUNNING": JobStatus.RUNNING,
    "COMPLETED": JobStatus.DONE,
    "FAILED": JobStatus.ERROR,
    "CANCELLING": JobStatus.RUNNING,
    "CANCELLED": JobStatus.CANCELLED,
    "UNKNOWN": JobStatus.INITIALIZING,
}


class PlanqkJob(JobV1):
    version = 1

    def __init__(self, backend: Optional[Backend], job_id: Optional[str] = None, job_details: Optional[JobDto] = None):

        if job_id is None and job_details is None:
            raise ValueError("Either 'job_id', 'job_details' or both must be provided.")

        self._result = None
        self._backend = backend
        self._job_details = job_details

        if job_id is not None and job_details is None:
            self._job_id = job_id
            self._refresh()
        elif job_id is None and job_details is not None:
            self.submit()
        else:
            self._job_id = job_id
            self._job_details = job_details

        job_details_dict = self._job_details.dict()
        super().__init__(backend=backend, job_id=self._job_id, **job_details_dict)

    def submit(self):
        """
        Submits the job for execution.
        """

        if self._job_details is None:
            raise RuntimeError("Cannot submit job as no job details are set.")

        self._job_details = _PlanqkClient.submit_job(self._job_details)
        self._job_id = self._job_details.id

    def result(self) -> Result:
        """
        Return the result of the job.
        """
        if self._result is not None:
            return self._result

        if not self.in_final_state():
            self.wait_for_final_state()

        status = JobStatusMap[self._job_details.status]
        if not status == JobStatus.DONE:
            raise RuntimeError(
                f'{"Cannot retrieve results as job execution did not complete successfully. "}'
                + f"(status: {self.status}."
                + f"error: {self.error_data})"
            )

        result_data = _PlanqkClient.get_job_result(self._job_id, self.backend().backend_provider)

        experiment_result = ExperimentResult(
            shots=self._job_details.shots,
            success=True,
            status=status,
            data=ExperimentResultData(
                counts=result_data["counts"] if result_data["counts"] is not None else {},
                memory=result_data["memory"] if result_data["memory"] is not None else []
            ),
            # Header required for PennyLane-Qiskit Plugin as it identifies the result based on the circuit name which is always "circ0"
            header=QobjExperimentHeader(name="circ0")
        )

        self._result = Result(
            backend_name=self._backend.name,
            backend_version=self._backend.version,
            job_id=self._job_id,
            qobj_id=0,
            success=True,
            results=[experiment_result],
            status=status,
            date=self._job_details.end_execution_time,
        )

        return self._result

    def _refresh(self):
        """
        Refreshes the job details from the server.
        """
        if self.job_id is None:
            raise ValueError("Job Id is not set.")
        self._job_details = _PlanqkClient.get_job(self._job_id, self.backend().backend_provider)

    def cancel(self):
        """
        Attempt to cancel the job.
        """
        _PlanqkClient.cancel_job(self._job_id, self.backend().backend_provider)

    def status(self) -> JobStatus:
        """
        Return the status of the job.
        """
        self._refresh()
        return JobStatusMap[self._job_details.status]

    @property
    def id(self):
        """
        This job's id.
        """
        return self._job_id

    def to_dict(self) -> dict:
        """
        Return a dictionary representation of the job.
        """
        return {key: value for key, value in vars(self).items() if not key.startswith('_')}
