##
# Updated version of azure.quantum.target.target_factory.TargetFactory for interacting with PlanQK backends.
##

import warnings
import asyncio
from typing import Any, Dict, List, TYPE_CHECKING, Union, Tuple
from azure.quantum.target import *
from azure.quantum._client import models
from azure.quantum.workspace import DEFAULT_CONTAINER_NAME_FORMAT
from msrest import Serializer, Deserializer

from planqk.client import PlanqkClient

if TYPE_CHECKING:
    from azure.quantum import Workspace
    from azure.quantum._client.models import TargetStatus

# Target ID keyword for parameter-free solvers
PARAMETER_FREE = "parameterfree"


class PlanqkTargetFactory:
    """Factory class for generating a Target based on a
    provider and target name
    """
    __instances = {}

    def __new__(cls, *args, **kwargs):
        base_cls = kwargs.get("base_cls")
        if cls.__instances.get(base_cls) is None:
            cls.__instances[base_cls] = super().__new__(cls)
        return cls.__instances[base_cls]

    def __init__(
            self,
            base_cls: Target,
            client: PlanqkClient,
            default_targets: Dict[str, Any] = DEFAULT_TARGETS,
            all_targets: Dict[str, Any] = None
    ):
        """Target factory class for creating targets
        based on a name and/or provider ID.

        :param base_cls: Base class for findng first and second
            generation child classes.
        :type base_cls: Target
        :param client: PlanQK Backend Client
        :type client: PlanqkClient
        :param default_targets: Dictionary of default target classes keyed
            by provider ID, defaults to DEFAULT_TARGETS
        :type default_targets: Dict[str, Any], optional
        :param all_targets: Dictionary of all target classes by name,
            optional. Defaults to finding all first and second degree
            subclasses of base_cls by name via cls.target_names.
        :type all_targets: Dict[str, Any]
        """
        self._base_cls = base_cls
        self._client = client
        # case insensitive lookup
        self._default_targets = {k.lower(): v for k, v in default_targets.items()}
        self._all_targets = all_targets or self._get_all_target_cls()

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)

    def _get_all_target_cls(self) -> Dict[str, Target]:
        """Get all target classes by target name"""
        return {
            name.lower(): _t for t in self._base_cls.__subclasses__()
            for _t in t.__subclasses__() + [t]
            if hasattr(_t, "target_names")
            for name in _t.target_names
            if not asyncio.iscoroutinefunction(_t.submit)
        }

    def _target_cls(self, provider_id: str, name: str):
        if name in self._all_targets:
            return self._all_targets[name.lower()]

        if provider_id.lower() in self._default_targets:
            return self._default_targets[provider_id.lower()]

        warnings.warn(
            f"No default target specified for provider {provider_id}. \
Please check the provider name and try again or create an issue here: \
https://github.com/microsoft/qdk-python/issues.")
        return Target

    def create_target(
            self, provider_id: str, name: str, **kwargs
    ) -> Target:
        """Create target from provider ID and target name.

        :param provider_id: Provider name
        :type provider_id: str
        :param name: Target name
        :type name: str
        :return: Target instance
        :rtype: Target
        """
        cls = self._target_cls(provider_id, name)
        if cls is not None:
            return cls(
                name=name,
                provider_id=provider_id,
                **kwargs
            )

    def from_target_status(
            self,
            provider_id: str,
            status: "TargetStatus",
            **kwargs
    ):
        cls = self._target_cls(provider_id, status.id)
        if hasattr(cls, "from_target_status"):
            return cls.from_target_status(self._workspace, status, **kwargs)
        elif cls is not None:
            return cls(name=status.id, **kwargs)

    def get_targets(
            self,
            name: str,
            provider_id: str,
            **kwargs
    ) -> Union[Target, List[Target]]:
        """Retrieve targets that are available in PlanQK
        filtered by name and provider ID.

        :param name: Target name
        :type name: str
        :param provider_id: Provider name
        :type provider_id: str
        :return: One or more Target objects
        :rtype: Union[Target, List[Target]]
        """
        target_statuses = self._get_target_status(name, provider_id)

        if len(target_statuses) == 1:
            return self.from_target_status(*target_statuses[0], **kwargs)

        else:
            # Don't return redundant parameter-free targets
            return [
                self.from_target_status(_provider_id, status, **kwargs)
                for _provider_id, status in target_statuses
                if PARAMETER_FREE not in status.id
                   and (
                           _provider_id.lower() in self._default_targets
                           or status.id in self._all_targets
                   )
            ]

    def _get_target_status(self, name: str, provider_id: str) -> List[Tuple[str, "TargetStatus"]]:
        """Get provider ID and status for targets"""
        response = self._client.get_backends()
        backends: object = self._deserialize_provider_status_list(response)

        return [
            (provider.id, target)
            for provider in backends
            for target in provider.targets
            if (provider_id is None or provider.id.lower() == provider_id.lower())
               and (name is None or target.id.lower() == name.lower())
        ]

    def _deserialize_provider_status_list(self, provider_status_list_json):
        deserialized = self._deserialize("ProviderStatusList", provider_status_list_json)
        list_of_elem = deserialized.value
        return iter(list_of_elem)