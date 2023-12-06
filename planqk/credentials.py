import json
import logging
import os
import platform
from abc import ABC, abstractmethod
from json import JSONDecodeError

from planqk.exceptions import CredentialUnavailableError

_PERSONAL_ACCESS_TOKEN_NAME = 'PLANQK_PERSONAL_ACCESS_TOKEN'
_SERVICE_EXECUTION_TOKEN_NAME = 'PLANQK_SERVICE_EXECUTION_TOKEN'
_SERVICE_EXECUTION_TOKEN_NAME_DEPRECATED = 'SERVICE_EXECUTION_TOKEN'
_CONFIG_FILE_PATH = 'PLANQK_CONFIG_FILE_PATH'

logger = logging.getLogger(__name__)


class CredentialProvider(ABC):
    @abstractmethod
    def get_access_token(self) -> str:
        pass


class EnvironmentCredential(CredentialProvider):
    def get_access_token(self) -> str:
        access_token = os.environ.get(_SERVICE_EXECUTION_TOKEN_NAME)
        # backwards compatibility, remove in future
        if not access_token:
            access_token = os.environ.get(_SERVICE_EXECUTION_TOKEN_NAME_DEPRECATED)
        if not access_token:
            access_token = os.environ.get(_PERSONAL_ACCESS_TOKEN_NAME)
        if not access_token:
            message = f'Environment variable {_PERSONAL_ACCESS_TOKEN_NAME} or {_SERVICE_EXECUTION_TOKEN_NAME} not set'
            raise CredentialUnavailableError(message)
        return access_token


def get_config_file_path():
    config_file_path = os.environ.get(_CONFIG_FILE_PATH, None)
    if not config_file_path:
        if platform.system() == 'Windows':
            config_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'planqk')
        else:
            config_dir = os.path.join(os.path.expanduser('~'), '.config', 'planqk')
        config_file_path = os.path.join(config_dir, 'config.json')
    return config_file_path


class ConfigFileCredential(CredentialProvider):
    def __init__(self):
        self.config_file = get_config_file_path()

    def get_access_token(self) -> str:
        if not self.config_file:
            raise CredentialUnavailableError('Config file location not set')
        if not os.path.isfile(self.config_file):
            raise CredentialUnavailableError(f'Config file at {self.config_file} does not exist')
        try:
            access_token = ConfigFileCredential.parse_file(self.config_file)
        except JSONDecodeError:
            raise CredentialUnavailableError('Failed to parse config file: Invalid JSON')
        except KeyError as e:
            raise CredentialUnavailableError(f'Failed to parse config file: Missing expected value - {str(e)}')
        except Exception as e:
            raise CredentialUnavailableError(f'Failed to parse config file: {str(e)}')
        return access_token

    @staticmethod
    def parse_file(path) -> str:
        with open(path, 'r') as file:
            data = json.load(file)
            return data['auth']['value']


class StaticCredential(CredentialProvider):
    def __init__(self, access_token=None):
        self.access_token = access_token

    def get_access_token(self) -> str:
        if not self.access_token:
            raise CredentialUnavailableError(f'Access token not set')
        return self.access_token


class DefaultCredentialsProvider(CredentialProvider):
    def __init__(self, access_token=None):
        self.credentials = [
            StaticCredential(access_token),
            EnvironmentCredential(),
            ConfigFileCredential(),
        ]

    def get_access_token(self) -> str:
        for credential in self.credentials:
            try:
                access_token = credential.get_access_token()
                logger.debug('%s acquired an access token from %s',
                             self.__class__.__name__, credential.__class__.__name__)
                return access_token
            except CredentialUnavailableError:
                logger.debug('%s - %s is unavailable', self.__class__.__name__, credential.__class__.__name__)
            except Exception as e:
                logger.error('%s.get_access_token() failed: %s raised unexpected error "%s"', self.__class__.__name__,
                             credential.__class__.__name__, e, exc_info=logger.isEnabledFor(logging.DEBUG))

        message = f'{self.__class__.__name__} failed to retrieve an access token'
        logger.warning(message)
        raise CredentialUnavailableError(message)
