from datetime import datetime
from typing import Optional, Type, Any, Callable, Dict

from qiskit.providers import Backend
from qiskit_ibm_runtime.program import ResultDecoder

from planqk.qiskit import PlanqkJob
from planqk.qiskit.client.job_dtos import JobDto


class PlanqkRuntimeJob(PlanqkJob):

    def __init__(self, backend: Optional[Backend], job_id: Optional[str] = None, job_details: Optional[JobDto] = None,
                 provider_token: str = None):
        super().__init__(backend, job_id, job_details, provider_token)
        self._session_id = self._job_details.input_params['session_id']
        self._program_id = self._job_details.input_params['program_id']

    def interim_results(self, decoder: Optional[Type[ResultDecoder]] = None) -> Any:
        raise NotImplementedError("Interim results are not supported for PlanQK runtime jobs.")

    def stream_results(
            self, callback: Callable, decoder: Optional[Type[ResultDecoder]] = None
    ) -> None:
        raise NotImplementedError("Result streaming is not supported for PlanQK runtime jobs.")

    def cancel_result_streaming(self) -> None:
        raise NotImplementedError("Canceling result streaming is not supported for PlanQK runtime jobs.")

    def logs(self) -> str:
        raise NotImplementedError("Logs are not supported for PlanQK runtime jobs.")

    def metrics(self) -> Dict[str, Any]:
        raise NotImplementedError("Metrics are not supported for PlanQK runtime jobs.")

    @property
    def image(self) -> str:
        """Return the runtime image used for the job.

        Returns:
            Runtime image: image_name:tag or "" if the default
            image is used.
        """
        raise NotImplementedError("Image is not supported for PlanQK runtime jobs.")

    @property
    def inputs(self) -> Dict:
        """Job input parameters.

        Returns:
            Input parameters used in this job.
        """
        raise NotImplementedError("Inputs are not supported for PlanQK runtime jobs.")

    @property
    def program_id(self) -> str:
        """Program ID.

        Returns:
            ID of the program this job is for.
        """
        return self._program_id

    @property
    def creation_date(self) -> Optional[datetime]:
        """Job creation date in local time.

        Returns:
            The job creation date as a datetime object, in local time, or
            ``None`` if creation date is not available.
        """
        raise NotImplementedError("Creation date is not supported for PlanQK runtime jobs.")

    @property
    def session_id(self) -> str:
        """Session ID.

        Returns:
            Job ID of the first job in a runtime session.
        """
        return self._session_id
