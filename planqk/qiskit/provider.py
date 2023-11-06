import json

from qiskit.providers import ProviderV1 as Provider, QiskitBackendNotFoundError

from planqk.credentials import DefaultCredentialsProvider
from planqk.exceptions import PlanqkClientError
from planqk.qiskit.backend import PlanqkBackend
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.client.client import _PlanqkClient


class PlanqkQuantumProvider(Provider):

    def __init__(self, access_token: str = None):
        """Initialize the PlanQK provider.
              Args:
                    access_token (str): access token used for authentication with PlanQK. If not token is provided,
                    the token is retrieved from the environment variable PLANQK_ACCESS_TOKEN that can be either set
                    manually or by using the PlanQK CLI.
        """
        _PlanqkClient.set_credentials(DefaultCredentialsProvider(access_token))

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

        return PlanqkBackend(
            backend_info=backend_dto,
            provider=self,
            name=backend_dto.id,
            description=f"PlanQK Backend: {backend_dto.hardware_provider.name} {backend_dto.id}.",
            online_date=backend_dto.updated_at,
            backend_version="2",
        )

    @staticmethod
    def get_access_token():
        """Returns the access token used for authentication with PlanQK."""
        return _PlanqkClient.get_credentials().get_access_token()

    @property
    def provider_token(self):
        return self._provider_token
