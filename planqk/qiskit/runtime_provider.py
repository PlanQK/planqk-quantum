import logging
import unittest
from typing import Optional, Union, Callable, Type, Sequence, Dict

from qiskit.providers import QiskitBackendNotFoundError
from qiskit_ibm_runtime import RuntimeOptions, ParameterNamespace, RuntimeJob
from qiskit_ibm_runtime.accounts import ChannelType
from qiskit_ibm_runtime.program import ResultDecoder

from planqk.qiskit import PlanqkQuantumProvider, PlanqkJob
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.client.client import _PlanqkClient
from planqk.qiskit.client.job_dtos import RuntimeJobParamsDto, JobDto, INPUT_FORMAT
from planqk.qiskit.providers.helper.job_input_converter import convert_circuit_to_backend_input

logger = logging.getLogger(__name__)


class PlanqkQiskitRuntimeService(PlanqkQuantumProvider):

    def __init__(self, access_token=None, channel: Optional[ChannelType] = None):
        super().__init__(access_token)

        self._channel = channel
        # Mock close_session method of API client as it is called by the session object after a program has run
        self._api_client = type('Mock_API_Client', (), {'close_session': lambda self: None})

        # self._account = self._discover_account(
        #     token=token,
        #     url=url,
        #     instance=instance,
        #     channel=channel,
        #     filename=filename,
        #     name=name,
        #     proxies=ProxyConfiguration(**proxies) if proxies else None,
        #     verify=verify,
        # )

        # TODO token

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
        backend = self.get_backend(name=name, provider=PROVIDER.IBM)

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

        input_params = runtime_job_params.to_dict()

        job_request = JobDto(backend_id,
                             provider=PROVIDER.IBM.name,
                             input_format=input_data[0],
                             input=input_data[1],
                             shots=shots,
                             input_params=input_params)

        # TODO return RuntimeJob
        return PlanqkJob(backend=backend, job_details=job_request)

        # _PlanqkClient.submit_job()
        #
        #
        # response = self._api_client.program_run(
        #     program_id=program_id,
        #     backend_name=qrt_options.backend,
        #     params=inputs,
        #     image=qrt_options.image,
        #     hgp=hgp_name,
        #     log_level=qrt_options.log_level,
        #     session_id=session_id,
        #     job_tags=qrt_options.job_tags,
        #     max_execution_time=qrt_options.max_execution_time,
        #     start_session=start_session,
        #     session_time=qrt_options.session_time,
        #
        #
        # backend = self.backend(name=response["backend"], instance=hgp_name)
        #
        # job = RuntimeJob(
        #     backend=backend,
        #     api_client=self._api_client,
        #     client_params=self._client_params,
        #     job_id=response["id"],
        #     program_id=program_id,
        #     params=inputs,
        #     user_callback=callback,
        #     result_decoder=result_decoder,
        #     image=qrt_options.image,
        #     service=self,
        # )
        # return job

    @property
    def channel(self) -> str:
        """Return the channel type used.

        Returns:
            The channel type used.
        """
        return self._channel
