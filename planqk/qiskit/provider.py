import json
from typing import List

from qiskit.providers import ProviderV1 as Provider, QiskitBackendNotFoundError

from planqk.credentials import DefaultCredentialsProvider
from planqk.exceptions import PlanqkClientError
from planqk.qiskit import PlanqkJob
from planqk.qiskit.backend import PlanqkBackend
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.client.client import _PlanqkClient


class PlanqkQuantumProvider(Provider):

    def __init__(self, access_token: str = None, organization_id: str = None):
        """Initialize the PlanQK provider.
              Args:
                    access_token (str): access token used for authentication with PlanQK. If not token is provided,
                    the token is retrieved from the environment variable PLANQK_ACCESS_TOKEN that can be either set
                    manually or by using the PlanQK CLI.
        """
        _PlanqkClient.set_credentials(DefaultCredentialsProvider(access_token))
        _PlanqkClient.set_organization_id(organization_id)

    def backends(self, provider: PROVIDER = None, **kwargs):
        """
        Return the list of backend ids supported by PlanQK.

           Args:

               name (str): name of the backend.

               **kwargs: dict used for filtering - currently not supported.

           Returns:

               List[Backend]: a list of Backends that match the filtering
                   criteria.
                   :param name:
                   :param provider: the provider of the backend
        """
        backend_dtos = _PlanqkClient.get_backends()

        supported_backend_ids = [
            backend_info.id for backend_info in backend_dtos
            if (provider is None or backend_info.provider == provider) and backend_info.provider != PROVIDER.DWAVE
        ]
        return supported_backend_ids

    def get_backend(self, name=None, provider: PROVIDER = None, **kwargs):
        """Return a single backend matching the specified filtering.

        Args:
            :param name: name of the backend.
            :param provider: the provider of the backend
            **kwargs: dict used for filtering.

        Returns:
            Backend: a backend matching the filtering.

        Raises:
            QiskitBackendNotFoundError: if no backend could be found or
                more than one backend matches the filtering criteria.

        """
        try:
            backend_dto = _PlanqkClient.get_backend(backend_id=name)
            if provider is not None and backend_dto.provider != provider:
                raise QiskitBackendNotFoundError(
                    "No backend matches the criteria. "
                    "Reason: Required provider {0} does not match with returned backend provider {1}.".format(
                        provider, backend_dto.provider))
        except PlanqkClientError as e:
            if e.response.status_code == 404:
                error_detail = json.loads(e.response.text)
                raise QiskitBackendNotFoundError(
                    "No backend matches the criteria. Reason: " + error_detail['error'])
            raise e

        backend_state_dto = _PlanqkClient.get_backend_state(backend_id=name)
        if backend_state_dto:
            backend_dto.status = backend_state_dto.status

        backend_init_params = {
            'backend_info': backend_dto,
            'provider': self,
            'name': backend_dto.id,
            'description': f"PlanQK Backend: {backend_dto.hardware_provider.name} {backend_dto.id}.",
            'online_date': backend_dto.updated_at,
            'backend_version': "2",
        }

        # add additional parameters to the backend init params
        backend_init_params.update(**kwargs)

        return self._get_backend_object(backend_dto, backend_init_params)

    def _get_backend_object(self, backend_dto, backend_init_params):
        if backend_dto.provider == PROVIDER.AWS:
            from planqk.qiskit.providers.aws.aws_backend import PlanqkAwsBackend
            return PlanqkAwsBackend(**backend_init_params)
        if backend_dto.provider == PROVIDER.AZURE:
            from planqk.qiskit.providers.azure.ionq_backend import PlanqkAzureIonqBackend
            return PlanqkAzureIonqBackend(**backend_init_params)
        elif backend_dto.provider == PROVIDER.QRYD:
            from planqk.qiskit.providers.qryd.qryd_backend import PlanqkQrydBackend
            return PlanqkQrydBackend(**backend_init_params)
        elif backend_dto.provider in {PROVIDER.IBM, PROVIDER.IBM_CLOUD}:
            from planqk.qiskit.providers.ibm.ibm_provider_backend import PlanqkIbmProviderBackend
            return PlanqkIbmProviderBackend(**backend_init_params)
        else:
            return QiskitBackendNotFoundError(
                f"Backends of provider '{backend_dto.provider}' are not supported.")

    def retrieve_job(self, backend: PlanqkBackend, job_id: str):
        """
        Retrieve a job from the backend.

        Args:
            backend (PlanqkBackend): the backend that run the job.
            job_id (str): the job id.

        Returns:
            Job: the job from the backend with the given id.
        """
        return PlanqkJob(backend=backend, job_id=job_id)

    def jobs(self) -> List[PlanqkJob]:
        """
        Returns all jobs of the user or organization.

        Returns:
            List[PlanqkJob]: a list of active jobs.
        """
        print("Getting your jobs from PlanQK, this may take a few seconds...")
        job_dtos = _PlanqkClient.get_jobs()
        return [PlanqkJob(backend=None, job_id=job_dto.id, job_details=job_dto) for job_dto in job_dtos]
