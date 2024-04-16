import logging
from datetime import datetime
from typing import Optional, Union, Callable, Type, Sequence, Dict, List, Any

from qiskit.providers import QiskitBackendNotFoundError
from qiskit_ibm_runtime import RuntimeOptions, ibm_backend
from qiskit_ibm_runtime.accounts import ChannelType
from qiskit_ibm_runtime.utils.result_decoder import ResultDecoder

from planqk.qiskit import PlanqkQuantumProvider
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.client.client import _PlanqkClient
from planqk.qiskit.client.job_dtos import RuntimeJobParamsDto, JobDto
from planqk.qiskit.planqk_runtime_job import PlanqkRuntimeJob

logger = logging.getLogger(__name__)


class PlanqkQiskitRuntimeService(PlanqkQuantumProvider):

    def __init__(self, access_token: Optional[str] = None,
                 organization_id: Optional[str] = None,
                 channel: Optional[ChannelType] = None,
                 channel_strategy=None):
        super().__init__(access_token, organization_id)

        self._channel = channel
        self._channel_strategy = channel_strategy
        # Mock close_session method of API client as it is called by the session object after a program has run
        self._api_client = type('Mock_API_Client', (), {'close_session': lambda self: None})

    def backend(
            self,
            name: str = None,
            instance: Optional[str] = None,
    ):
        """Return a single backend matching the specified filtering.

        Args:
            name: Name of the backend.
            instance: This is only supported for ``ibm_quantum`` runtime and is in the
                hub/group/project format. If an instance is not given, among the providers
                with access to the backend, a premium provider will be priotized.
                For users without access to a premium provider, the default open provider will be used.

        Returns:
            The id of : A backend matching the filtering.

        Raises:
            QiskitBackendNotFoundError: if no backend could be found.
        """
        # Backend returned must be from IBM
        backend = self.get_backend(name=name)
        if backend.backend_provider not in {PROVIDER.IBM, PROVIDER.IBM_CLOUD, PROVIDER.TSYSTEMS}:
            raise QiskitBackendNotFoundError(
                f"Backend '{name}' is not from IBM. Qiskit Runtime only supports IBM backends.")

        return backend

    def _get_backend_object(self, backend_dto, backend_init_params):
        if backend_dto.provider in {PROVIDER.IBM, PROVIDER.IBM_CLOUD, PROVIDER.TSYSTEMS}:
            from planqk.qiskit.providers.ibm.ibm_runtime_backend import PlanqkIbmRuntimeBackend
            return PlanqkIbmRuntimeBackend(**backend_init_params)
        else:
            return QiskitBackendNotFoundError(
                f"Backends of provider '{backend_dto.provider}' are not supported.")

    def run(self,
            program_id: str,
            inputs: Dict,
            options: Optional[Union[RuntimeOptions, Dict]] = None,
            callback: Optional[Callable] = None,
            result_decoder: Optional[Union[Type[ResultDecoder], Sequence[Type[ResultDecoder]]]] = None,
            session_id: Optional[str] = None,
            start_session: Optional[bool] = False, ):  # TODO return planqkjob

        qrt_options: RuntimeOptions = options
        if options is None:
            qrt_options = RuntimeOptions()
        elif isinstance(options, Dict):
            qrt_options = RuntimeOptions(**options)

        qrt_options.validate(channel=self.channel)

        hgp_name = 'ibm-q/open/main'

        runtime_job_params = RuntimeJobParamsDto(
            program_id=program_id,
            image=qrt_options.image,
            hgp=hgp_name,
            log_level=qrt_options.log_level,
            session_id=session_id,
            max_execution_time=qrt_options.max_execution_time,
            start_session=start_session,
            session_time=qrt_options.session_time,
        )

        backend_id = options.get('backend')
        backend = self.backend(backend_id)

        run_options = inputs.get('run_options')
        if run_options is None:
            shots = backend.min_shots
        else:
            shots = run_options.get('shots', backend.min_shots)

        job_input_format = backend.get_job_input_format()
        input_data = backend.convert_to_job_input(inputs)
        input_params = runtime_job_params.dict()

        job_request = JobDto(backend_id=backend_id,
                             provider=PROVIDER.IBM.name,
                             input_format=job_input_format,
                             input=input_data,
                             shots=shots,
                             input_params=input_params)

        return PlanqkRuntimeJob(backend=backend, job_details=job_request, result_decoder=result_decoder)

    @staticmethod
    def delete_account(
            filename: Optional[str] = None,
            name: Optional[str] = None,
            channel: Optional[ChannelType] = None,
    ) -> bool:
        raise NotImplementedError("Deleting an account is not supported.")

    @staticmethod
    def save_account(
            token: Optional[str] = None,
            url: Optional[str] = None,
            instance: Optional[str] = None,
            channel: Optional[ChannelType] = None,
            filename: Optional[str] = None,
            name: Optional[str] = None,
            proxies: Optional[dict] = None,
            verify: Optional[bool] = None,
            overwrite: Optional[bool] = False,
    ) -> None:
        raise NotImplementedError("Saving an account is not supported.")

    @staticmethod
    def saved_accounts(
            default: Optional[bool] = None,
            channel: Optional[ChannelType] = None,
            filename: Optional[str] = None,
            name: Optional[str] = None,
    ) -> dict:
        raise NotImplementedError("Listing saved accounts is not supported.")

    def job(self, job_id: str) -> PlanqkRuntimeJob:
        """Retrieve a runtime job.

                Args:
                    job_id: Job ID.

                Returns:
                    Runtime job retrieved.
                Raises:
                    PlanqkClientError: If the job cannot be retrieved.
                """
        job_details = _PlanqkClient.get_job(job_id)
        backend = self.get_backend(job_details.backend_id)

        return PlanqkRuntimeJob(backend=backend, job_id=job_id, job_details=job_details)

    def jobs(
            self,
            limit: Optional[int] = 10,
            skip: int = 0,
            backend_name: Optional[str] = None,
            pending: bool = None,
            program_id: str = None,
            instance: Optional[str] = None,
            job_tags: Optional[List[str]] = None,
            session_id: Optional[str] = None,
            created_after: Optional[datetime] = None,
            created_before: Optional[datetime] = None,
            descending: bool = True,
    ) -> List[PlanqkRuntimeJob]:
        raise NotImplementedError("Retrieving runtime jobs is not supported.")

    def delete_job(self, job_id: str) -> None:
        """Delete a runtime job.

        Note that this operation cannot be reversed.

        Args:
            job_id: ID of the job to delete.

        Raises:
            PlanqkClientError: If the job cannot be deleted.
        """
        job = self.job(job_id)
        job.cancel()

    def least_busy(
            self,
            min_num_qubits: Optional[int] = None,
            instance: Optional[str] = None,
            filters: Optional[Callable[[List["ibm_backend.IBMBackend"]], bool]] = None,
            **kwargs: Any,
    ) -> ibm_backend.IBMBackend:
        raise NotImplementedError("Retrieving the least busy backend is not supported.")

    @property
    def auth(self) -> str:
        raise NotImplementedError("Retrieving the authentication type is not supported.")

    @property
    def channel(self) -> str:
        """Return the channel type used.

        Returns:
            The channel type used.
        """
        return self._channel

    @property
    def runtime(self):  # type:ignore
        """Return self for compatibility with IBMQ provider.

        Returns:
            self
        """
        return self
