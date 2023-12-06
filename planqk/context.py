import os
from typing import Union

from pydantic import BaseModel, Field

from planqk.credentials import get_config_file_path


class Context(BaseModel):
    id: str = Field(description="Id of the user or organization")
    displayName: str = Field(description="Name of the user or organization")
    isOrganization: bool = Field(description="True if the context is an organization")


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
