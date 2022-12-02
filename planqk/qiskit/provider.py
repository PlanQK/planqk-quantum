import logging

from qiskit.providers import ProviderV1 as Provider

from planqk.client import PlanqkClient, PlanqkJob
from planqk.credentials import DefaultCredentialsProvider
from planqk.qiskit.provider_impls.azure.planqk_azure_provider import PlanqkAzureQuantumProvider
from planqk.qiskit.provider_impls.azure.workspace_proxy import WorkspaceProxy

logger = logging.getLogger(__name__)


class PlanqkQuantumProvider(Provider):

    def __init__(self, access_token=None):
        self._credentials = DefaultCredentialsProvider(access_token)
        self._client = PlanqkClient(self._credentials)

        workspace = WorkspaceProxy(self._client)

        azure_provider = PlanqkAzureQuantumProvider(
            client=self._client
        )

        self._providers = [azure_provider]

    def append_user_agent(self, value: str):
        pass

    def backends(self, name=None, **kwargs):
        backends = []

        for provider in self._providers:

            for backend in provider.backends(name, **kwargs):
                #TODO if azure provider
                #planqk_azure_backend = type("PlanQKAzureBackend", (AzureBackendProxy, type(backend),), {}) backend.configuration()
                #planqk_azure_backend_obj = planqk_azure_backend(backend.name(), provider)
                backends.append(backend)
                #TODO


        # jo = dir(backends[0])
        #
        # new_class = type("NewClassName", (type(backends[0]),), {"new_method": chuck})
        # inst = new_class("name", "provider")
        # inst.new_method() dir(inst)
        return backends


