import logging

from qiskit.providers import ProviderV1 as Provider

from planqk.client import PlanqkClient
from planqk.credentials import DefaultCredentialsProvider
from planqk.qiskit.backend import PlanqkQuantumBackend

logger = logging.getLogger(__name__)


class PlanqkQuantumProvider(Provider):

    def __init__(self, access_token=None):
        self._credentials = DefaultCredentialsProvider(access_token)
        self._client = PlanqkClient(self._credentials)

    def backends(self, name=None, **kwargs):
        targets = self._client.get_backends()
        try:
            idx = targets.index(name)
        except ValueError:
            return []
        target = targets[idx]
        if target is None:
            return []
        return [PlanqkQuantumBackend(client=self._client, backend_name=target, provider=self)]
