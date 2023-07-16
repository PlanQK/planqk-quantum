import logging
from datetime import datetime

from qiskit.providers import ProviderV1 as Provider

from planqk.credentials import DefaultCredentialsProvider
from planqk.qiskit.backend import PlanqkBackend
from planqk.qiskit.client.backend_dtos import TYPE
from planqk.qiskit.client.client import _PlanqkClient

class PlanqkQuantumProvider(Provider):

    def __init__(self, access_token=None):
        """Initialize the PlanQK provider.
              Args:
                    access_token (str): access token used for authentication with PlanQK. If not token is provided,
                    the token is retrieved from the environment variable PLANQK_ACCESS_TOKEN that can be either set
                    manually or by using the PlanQK CLI.
        """
        _PlanqkClient.set_credentials(DefaultCredentialsProvider(access_token))

    def backends(self, name=None, **kwargs):
        """
        Return the list of backends supported by PlanQK.

           Args:

               name (str): name of the backend.

               **kwargs: dict used for filtering - currently not supported.

           Returns:

               List[Backend]: a list of Backends that match the filtering
                   criteria.
        """

        backend_dtos = _PlanqkClient.get_backends(name)

        # only gate models are supported
        supported_backend_infos = [
            backend_info for backend_info in backend_dtos
            if backend_info.type == TYPE.QPU or backend_info.type == TYPE.SIMULATOR
        ]

        backends = []
        for backend_dto in supported_backend_infos:
            backends.append(
                PlanqkBackend(
                    backend_info=backend_dto,
                    provider=self,
                    name=backend_dto.name,
                    description=f"PlanQK Backend: {backend_dto.hardware_provider.name} {backend_dto.name}.",
                    online_date=datetime.strptime(backend_dto.updated_at, "%Y-%m-%d %H:%M:%S"),
                    backend_version="2",
                )
            )
        return backends

    @staticmethod
    def get_access_token():
        """Returns the access token used for authentication with PlanQK."""
        return _PlanqkClient.get_credentials().get_access_token()