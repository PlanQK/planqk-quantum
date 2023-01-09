import time

from planqk.client import logger, PlanqkClient

DEFAULT_TIMEOUT = 300  # Default timeout for waiting for job to complete


class ErrorData(object):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


def _json_dict_to_params(job_details_dict):
    return dict(provider_id=job_details_dict['provider_id'],
                target=job_details_dict['target'],
                input_data_format=job_details_dict['input_data_format'],
                job_id=job_details_dict['id'],
                input_data=job_details_dict.get('input_data_format', None),
                name=job_details_dict.get('name', None),
                input_params=job_details_dict.get('input_params', None),
                metadata=job_details_dict.get('metadata', None),
                output_data_format=job_details_dict.get('output_data_format', None),
                output_data=job_details_dict.get('output_data', None),
                status=job_details_dict.get('status', None),
                creation_time=job_details_dict.get('creation_time', None),
                begin_execution_time=job_details_dict.get('begin_execution_time', None),
                end_execution_time=job_details_dict.get('end_execution_time', None),
                cancellation_time=job_details_dict.get('cancellation_time', None),
                error_data=job_details_dict.get('error_data', None))


class PlanqkJob(object):
    def __init__(self, client: PlanqkClient, job_id: str = None, **job_details):
        self._client = client
        self.output_data = None

        if job_id is not None:
            self.job_id = job_id
            self.refresh()
        else:
            self._update_job_details(job_id=job_id, **job_details)

    def submit(self):
        """ Submits the job for execution. """
        job_details_dict = self._client.submit_job(self)
        self._update_job_details(**_json_dict_to_params(job_details_dict))

    def _update_job_details(self,
                            provider_id: str,
                            target: str,
                            input_data_format: str,
                            job_id: str = None,
                            input_data: str = None,
                            name: str = None,
                            input_params: object = None,
                            metadata: dict[str, str] = None,
                            output_data_format: str = None,
                            output_data: object = None,
                            status: str = None,
                            creation_time: str = None,
                            begin_execution_time: str = None,
                            end_execution_time: str = None,
                            cancellation_time: str = None,
                            tags: list[str] = [],
                            error_data: ErrorData = None):

        self.job_id = job_id
        self.name = name
        self.input_data_format = input_data_format
        self.input_data = input_data
        self.input_params = input_params
        self.provider_id = provider_id
        self.target = target
        self.metadata = metadata
        self.output_data = output_data
        self.output_data_format = output_data_format
        self.status = status
        self.creation_time = creation_time
        self.begin_execution_time = begin_execution_time
        self.end_execution_time = end_execution_time
        self.cancellation_time = cancellation_time
        self.tags = tags
        self.error_data = error_data

    def wait_until_completed(
            self,
            max_poll_wait_secs=30,
            timeout_secs=None,
            print_progress=True
    ) -> None:
        """Keeps refreshing the Job's details
        until it reaches a finished status.

        :param max_poll_wait_secs: Maximum poll wait time, defaults to 30
        :type max_poll_wait_secs: int, optional
        :param timeout_secs: Timeout in seconds, defaults to None
        :type timeout_secs: int, optional
        :param print_progress: Print "." to stdout to display progress
        :type print_progress: bool, optional
        :raises TimeoutError: If the total poll time exceeds timeout, raise
        """
        self.refresh()
        poll_wait = 0.2
        total_time = 0.
        while not self.has_completed():
            if timeout_secs is not None and total_time >= timeout_secs:
                raise TimeoutError(f"The wait time has exceeded {timeout_secs} seconds.")

            logger.debug(
                f"Waiting for job {self.id},"
                + f"it is in status '{self.status}'"
            )
            if print_progress:
                print(".", end="", flush=True)
            time.sleep(poll_wait)
            total_time += poll_wait
            self.refresh()
            poll_wait = (
                max_poll_wait_secs
                if poll_wait >= max_poll_wait_secs
                else poll_wait * 1.5
            )

    def has_completed(self) -> bool:
        """Check if the job has completed."""

        return (
                self.status == "Succeeded"
                or self.status == "Failed"
                or self.status == "Cancelled"
        )

    def refresh(self):
        """ Refreshes the job metadata from the server."""
        job_details_dict = self._client.get_job(self.job_id)
        self._update_job_details(**_json_dict_to_params(job_details_dict))

    def cancel(self):
        """Attempt to cancel the job."""
        self._client.cancel_job(self.job_id)

    def results(self, timeout_secs: float = DEFAULT_TIMEOUT) -> dict:
        """Return the results of the job."""
        if self.output_data is not None:
            return self.output_data

        if not self.has_completed():
            self.wait_until_completed(timeout_secs=timeout_secs)

        if not self.status == "Succeeded":
            raise RuntimeError(
                f'{"Cannot retrieve results as job execution failed"}'
                + f"(status: {self.status}."
                + f"error: {self.error_data})"
            )

        self.output_data = self._client.get_job_result(self.job_id)

        return self.output_data

    def to_dict(self) -> dict:
        # Create dict and remove private fields
        return {key: value for key, value in vars(self).items() if not key.startswith('_')}

    @property
    def id(self):
        """ This job's id."""
        return self.job_id
