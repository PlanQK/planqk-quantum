from azure.quantum import Workspace, Job
from typing import Any, Dict, Iterable, List, Optional, TYPE_CHECKING, Tuple, Union

from azure.quantum._client import models
from azure.quantum.workspace import DEFAULT_CONTAINER_NAME_FORMAT
from msrest import Serializer, Deserializer

from planqk.client import PlanqkClient, PlanqkJob


class WorkspaceProxy(Workspace):
    # TODO Document me
    def __init__(self, client: PlanqkClient):
        self._client = client

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)

    def _get_target_status(self, name: str, provider_id: str) -> List[Tuple[str, "TargetStatus"]]:
        """Get provider ID and status for targets"""
        backendProvidersResponse = self._client.get_backends()
        backends: object = self._deserialize_provider_status_list(backendProvidersResponse)

        return [
            (provider.id, target)
            for provider in backends
            for target in provider.targets
            if (provider_id is None or provider.id.lower() == provider_id.lower())
               and (name is None or target.id.lower() == name.lower())
        ]

    def append_user_agent(self, value: str):
        pass

    def submit_job(self, job: Job) -> Job:
        create_job_request = PlanqkJob(
            provider_id=job.details.provider_id,
            name=job.details.name,
            input_data=job.details.container_uri,
            input_data_format=job.details.input_data_format,
            input_params=job.details.input_params,
            povider_id=job.details.provider_id,
            target=job.details.target,
            meta_data=job.details.metadata,
            output_data_format=job.details.output_data_format
        )
        details = self._client.submit_job(create_job_request)
        return Job(self, details)

    def get_container_uri(
            self,
            job_id: str = None,
            container_name: str = None,
            container_name_format: str = DEFAULT_CONTAINER_NAME_FORMAT
    ) -> str:
        return "https://planqk.de/myJob"

    def _deserialize_provider_status_list(self, provider_status_list_json):
        deserialized = self._deserialize("ProviderStatusList", provider_status_list_json)
        list_of_elem = deserialized.value
        return iter(list_of_elem)
