from typing import Optional

from qiskit.providers import JobV1, JobStatus, Backend
from qiskit.result import Result
from qiskit.result.models import ExperimentResult, ExperimentResultData

from planqk.qiskit.client.client import _PlanqkClient
from planqk.qiskit.client.client_dtos import JobDto


class ErrorData(object):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


JobStatusMap = {
    "CREATED": JobStatus.INITIALIZING,
    "PENDING": JobStatus.QUEUED,
    "RUNNING": JobStatus.RUNNING,
    "COMPLETED": JobStatus.DONE,
    "FAILED": JobStatus.ERROR,
    "CANCELLING": JobStatus.RUNNING,
    "CANCELLED": JobStatus.CANCELLED,
}


class PlanqkJob(JobV1):
    version = 1

    def __init__(self, backend: Optional[Backend], job_id: Optional[str] = None, job_details: Optional[JobDto] = None):

        if job_id is None and job_details is None:
            raise ValueError("Either 'job_id' or 'job_details' must be provided.")
        if job_id is not None and job_details is not None:
            raise ValueError("Only one of 'job_id' or 'job_details' can be provided.")

        self._result = None
        self._backend = backend
        self._job_details = job_details

        if job_id is not None:
            self._job_id = job_id
            self._refresh()
            # TODO get backend from job details bakcend id

        else:
            self.submit()

        job_details_dict = self._job_details.to_dict()
        super().__init__(backend=backend, job_id=self._job_id, **job_details_dict)

    def submit(self):
        """
        Submits the job for execution.
        """

        if self._job_details is None:
            raise RuntimeError("Cannot submit job as no job details are set.")

        self._job_id = _PlanqkClient.submit_job(self._job_details)

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
                f'{"Cannot retrieve results as job execution failed"}'
                + f"(status: {self.status}."
                + f"error: {self.error_data})"
            )

        result_data = _PlanqkClient.get_job_result(self._job_id)

        experiment_result = ExperimentResult(
            shots=self._job_details.shots,
            success=True,
            status=status,
            data=ExperimentResultData(
                counts=result_data.get("counts", {}),
                memory=result_data.get("memory", []))
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
        self._job_details = _PlanqkClient.get_job(self._job_id)

    def cancel(self):
        """
        Attempt to cancel the job.
        """
        _PlanqkClient.cancel_job(self._job_id)

    def status(self) -> JobStatus:
        """
        Return the status of the job if it has reached the state DONE. If it is still running, it polls for the result.
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
