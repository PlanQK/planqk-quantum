import logging
from datetime import datetime

from qiskit.providers import ProviderV1 as Provider

from planqk.credentials import DefaultCredentialsProvider
from planqk.qiskit.backend import PlanqkBackend
from planqk.qiskit.client.backend_dtos import TYPE
from planqk.qiskit.client.client import _PlanqkClient

logger = logging.getLogger(__name__)


class PlanqkQuantumProvider(Provider):

    def __init__(self, access_token=None):
        _PlanqkClient.set_credentials(DefaultCredentialsProvider(access_token))

    def backends(self, name=None, **kwargs):
        """Return a list of backends matching the specified filtering.
           Args:
               name (str): name of the backend.
               **kwargs: dict used for filtering.
           Returns:
               List[Backend]: a list of Backends that match the filtering
                   criteria.
        """

        # if kwargs.get("local"):  # TODO local backend
        #   return [BraketLocalBackend(name="default")]

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

    def get_job(self, job_id):
        """ Returns the Job instance associated with the given id."""
        for provider in self._providers:
            job = provider.get_job(job_id)
            if job is not None:
                return job
