import logging

from qiskit.providers import ProviderV1 as Provider

from anaqor.client import AnaqorClient
from anaqor.credentials import DefaultCredentialsProvider
from anaqor.qiskit.backend import AnaqorQuantumBackend

logger = logging.getLogger(__name__)


class AnaqorQuantumProvider(Provider):

    def __init__(self, access_token=None):
        self._credentials = DefaultCredentialsProvider(access_token)
        self._client = AnaqorClient(self._credentials)

    def backends(self, name=None, **kwargs):
        targets = self._client.get_backends()
        try:
            idx = targets.index(name)
        except ValueError:
            return []
        target = targets[idx]
        if target is None:
            return []
        return [AnaqorQuantumBackend(client=self._client, backend_name=target, provider=self)]
