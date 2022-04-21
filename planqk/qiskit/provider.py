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
        backends = self._client.get_backends()
        targets = []

        if name is None:
            for backend_name in backends:
                target = PlanqkQuantumBackend(client=self._client, backend_name=backend_name, provider=self)
                targets.append(target)
        else:
            try:
                idx = backends.index(name)
            except ValueError:
                return []
            backend_name = backends[idx]
            if backend_name is None:
                return []
            target = PlanqkQuantumBackend(client=self._client, backend_name=backend_name, provider=self)
            targets.append(target)

        return targets
