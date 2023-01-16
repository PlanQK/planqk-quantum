from typing import Iterable

from azure.quantum.target import Target
from qiskit.providers import ProviderV1 as Provider
from qiskit.providers.exceptions import QiskitBackendNotFoundError

from planqk.client import PlanqkClient
from planqk.qiskit.job import PlanqkJob
from planqk.qiskit.providers.azure.planqk_azure_backend import PlanqkAzureBackend
from planqk.qiskit.providers.azure.planqk_azure_job import PlanqkAzureJob
from planqk.qiskit.providers.azure.planqk_target_factory import PlanqkTargetFactory

QISKIT_USER_AGENT = "azure-quantum-qiskit"


class PlanqkAzureQuantumProvider(Provider):

    def __init__(self, client: PlanqkClient):
        self._backends = None
        self._client = client

    def _get_all_subclasses(self, cls):
        all_subclasses = []
        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(self._get_all_subclasses(subclass))
        return all_subclasses

    def get_backend(self, name=None, **kwargs):
        """
        Return a single backend matching the specified filtering.

        Args:
            name (str): name of the backend.

        Returns:
            Backend: a backend matching the filtering.

        Raises:
            QiskitBackendNotFoundError: if no backend could be found or
                more than one backend matches the filtering criteria.
        """
        backends = self.backends(name, **kwargs)
        if len(backends) > 1:
            raise QiskitBackendNotFoundError("More than one backend matches the criteria")
        if not backends:
            raise QiskitBackendNotFoundError(f"Could not find backend '{name}'. \
                Please make sure the target name is valid.")
        return backends[0]

    def backends(self, name=None, provider_id=None, **kwargs):
        """
        Return a list of backends matching the specified filtering.

        Args:
            name (str): name of the backend.
            provider_id (str): Provider name
            **kwargs: dict used for filtering.
        Returns:
            list[Backend]: a list of Backends that match the filtering
                criteria.
        """
        from qiskit.providers import BackendV1 as Backend
        from azure.quantum.qiskit.backends import DEFAULT_TARGETS

        all_targets = {
            name: _t for t in self._get_all_subclasses(Backend)
            for _t in [t]
            if hasattr(_t, "backend_names")
            for name in _t.backend_names
        }

        target_factory = PlanqkTargetFactory(
            base_cls=Backend,
            client=self._client,
            default_targets=DEFAULT_TARGETS,
            all_targets=all_targets
        )

        targets = target_factory.get_targets(
            name=name,
            provider_id=provider_id,
            provider=self,
            **kwargs
        )

        # Always return an iterable
        if isinstance(targets, Iterable):
            return [self._create_planqk_backend(target)
                    for target in targets]
        return [self._create_planqk_backend(targets)]

    def _create_planqk_backend(self, target: Target):
        return PlanqkAzureBackend(self._client, target)

    def get_job(self, job_id) -> PlanqkAzureJob:
        """
        Returns the Job instance associated with the given id.
        """
        job_dict = self._client.get_job(job_id)
        job = PlanqkJob(self._client, job_id, **job_dict)
        backend = self.get_backend(job.target)

        return PlanqkAzureJob(self._client, backend, job)
