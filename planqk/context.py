import os
from typing import Union

from pydantic import BaseModel, Field

from planqk.credentials import get_config_file_path

_ORGANIZATION_ID = "PLANQK_ORGANIZATION_ID"


class Context(BaseModel):
    id: str = Field(..., description="Id of the user or organization")
    display_name: str = Field(..., alias="displayName", description="Name of the user or organization")
    is_organization: bool = Field(..., alias="isOrganization", description="True if the context is an organization")

    def get_organization_id(self) -> Union[str, None]:
        organization_id = os.environ.get(_ORGANIZATION_ID, None)
        if organization_id:
            return organization_id

        if self.is_organization:
            return self.id
        return None


class Config(BaseModel):
    context: Context = Field(None, description="Context of the user or organization")


class ContextResolver:
    def __init__(self):
        self.config_file = get_config_file_path()

    def get_context(self) -> Union[Context, None]:
        if not os.path.isfile(self.config_file):
            return None

        config = Config.parse_file(self.config_file)
        return config.context
