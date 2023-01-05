import logging

from qiskit.providers import ProviderV1 as Provider

from planqk.client import PlanqkClient
from planqk.credentials import DefaultCredentialsProvider
from planqk.qiskit.providers.azure.planqk_azure_provider import PlanqkAzureQuantumProvider

logger = logging.getLogger(__name__)


class PlanqkQuantumProvider(Provider):

    def __init__(self, access_token=None):
        self._credentials = DefaultCredentialsProvider(access_token)
        self._client = PlanqkClient(self._credentials)

        azure_provider = PlanqkAzureQuantumProvider(
            client=self._client
        )

        self._providers = [azure_provider]

    def backends(self, name=None, **kwargs):
        backends = []

        for provider in self._providers:

            for backend in provider.backends(name, **kwargs):
                backends.append(backend)

        return backends


