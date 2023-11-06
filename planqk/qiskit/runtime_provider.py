import logging
from datetime import datetime
from typing import Optional, Union, Callable, Type, Sequence, Dict, List, Any

from qiskit.providers import QiskitBackendNotFoundError
from qiskit_ibm_runtime import RuntimeOptions, ParameterNamespace, RuntimeProgram, ibm_backend
from qiskit_ibm_runtime.accounts import ChannelType
from qiskit_ibm_runtime.program import ResultDecoder

from planqk.qiskit import PlanqkQuantumProvider
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.client.client import _PlanqkClient
from planqk.qiskit.client.job_dtos import RuntimeJobParamsDto, JobDto, INPUT_FORMAT
from planqk.qiskit.planqk_runtime_job import PlanqkRuntimeJob
from planqk.qiskit.providers.job_input_converter import convert_circuit_to_backend_input

logger = logging.getLogger(__name__)


class PlanqkQiskitRuntimeService(PlanqkQuantumProvider):

    def __init__(self, access_token=None, channel: Optional[ChannelType] = None, channel_strategy=None):
        super().__init__(access_token)

        self._channel = channel
        self._channel_strategy = channel_strategy
        # Mock close_session method of API client as it is called by the session object after a program has run
        self._api_client = type('Mock_API_Client', (), {'close_session': lambda self: None})

    def backend(
            self,
            name: str = None,
            instance: Optional[str] = None,
    ) -> str:
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
        if backend.backend_provider not in {PROVIDER.IBM, PROVIDER.IBM_CLOUD}:
            raise QiskitBackendNotFoundError(
                f"Backend '{name}' is not from IBM. Qiskit Runtime only supports IBM backends.")

        return backend

    def run(self,
            program_id: str,
            inputs: Union[Dict, ParameterNamespace],
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

        # If using params object, extract as dictionary.
        if isinstance(inputs, ParameterNamespace):
            inputs.validate()
            inputs = vars(inputs)

        qrt_options.validate(channel=self.channel)

        hgp_name = 'ibm-q/open/main'  # TODO determine dynamically
        # if self._channel == "ibm_quantum":
        #     # Find the right hgp
        #     hgp = self._get_hgp(instance=qrt_options.instance, backend_name=qrt_options.backend)
        #     hgp_name = hgp.name
        # backend = self.backend(name=qrt_options.backend, instance=hgp_name)
        # status = backend.status()
        # if status.operational is True and status.status_msg != "active":
        #     logger.warning(
        #         f"The backend {backend.name} currently has a status of {status.status_msg}."
        #     )
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

        input_data = convert_circuit_to_backend_input([INPUT_FORMAT.QISKIT_PRIMITIVE], inputs)

        backend_id = options.get('backend')
        backend = self.backend(backend_id)

        run_options = inputs.get('run_options')
        if run_options is None:
            shots = backend.min_shots
        else:
            shots = run_options.get('shots', backend.min_shots)

        input_params = runtime_job_params.dict()

        job_request = JobDto(backend_id=backend_id,
                             provider=PROVIDER.IBM.name,
                             input_format=input_data[0],
                             input=input_data[1],
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

    def pprint_programs(
            self,
            refresh: bool = False,
            detailed: bool = False,
            limit: int = 20,
            skip: int = 0,
    ) -> None:
        raise NotImplementedError("Pretty print information about available runtime programs is not supported.")

    def programs(
            self, refresh: bool = False, limit: int = 20, skip: int = 0
    ) -> List[RuntimeProgram]:
        raise NotImplementedError("Listing available runtime programs is not supported.")

    def program(self, program_id: str, refresh: bool = False) -> RuntimeProgram:
        raise NotImplementedError("Retrieving a runtime program is not supported.")

    def upload_program(self, data: str, metadata: Optional[Union[Dict, str]] = None) -> str:
        raise NotImplementedError("Uploading a runtime program is not supported.")

    def update_program(
            self,
            program_id: str,
            data: str = None,
            metadata: Optional[Union[Dict, str]] = None,
            name: str = None,
            description: str = None,
            max_execution_time: int = None,
            spec: Optional[Dict] = None,
    ) -> None:
        raise NotImplementedError("Updating a runtime program is not supported.")

    def delete_program(self, program_id: str) -> None:
        raise NotImplementedError("Deleting a runtime program is not supported.")

    def set_program_visibility(self, program_id: str, public: bool) -> None:
        raise NotImplementedError("Setting the visibility of a runtime program is not supported.")

    def job(self, job_id: str) -> PlanqkRuntimeJob:
        """Retrieve a runtime job.

                Args:
                    job_id: Job ID.

                Returns:
                    Runtime job retrieved.
                Raises:
                    PlanqkClientError: If the job cannot be retrieved.
                """
        job_details = _PlanqkClient.get_job(job_id, PROVIDER.IBM)
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
