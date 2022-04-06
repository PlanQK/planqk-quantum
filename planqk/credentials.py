import json
import logging
import os
from abc import ABC, abstractmethod
from json import JSONDecodeError

from planqk.exceptions import CredentialUnavailableError, PlanqkClientError

_TOKEN_ENV_VARIABLE = 'PLANQK_QUANTUM_ACCESS_TOKEN'
_TOKEN_FILE_ENV_VARIABLE = 'PLANQK_QUANTUM_ACCESS_TOKEN_FILE'

logger = logging.getLogger(__name__)


class CredentialProvider(ABC):

    @abstractmethod
    def get_access_token(self) -> str:
        pass


class EnvironmentCredential(CredentialProvider):

    def get_access_token(self) -> str:
        access_token = os.environ.get(_TOKEN_ENV_VARIABLE)
        if not access_token:
            raise CredentialUnavailableError(f'Environment variable {_TOKEN_ENV_VARIABLE} not set')
        return access_token


class TokenFileCredential(CredentialProvider):

    def get_access_token(self) -> str:
        access_token_file = os.environ.get(_TOKEN_FILE_ENV_VARIABLE)
        if not access_token_file:
            raise CredentialUnavailableError('Access Token file location not set')
        if not os.path.isfile(access_token_file):
            raise CredentialUnavailableError(f'Access Token file at {access_token_file} does not exist')
        try:
            access_token = TokenFileCredential.parse_access_token_file(access_token_file)
        except JSONDecodeError:
            raise CredentialUnavailableError('Failed to parse Access Token file: Invalid JSON')
        except KeyError as e:
            raise CredentialUnavailableError(f'Failed to parse Access Token file: Missing expected value - {str(e)}')
        except Exception as e:
            raise CredentialUnavailableError(f'Failed to parse Access Token file: {str(e)}')
        return access_token

    @staticmethod
    def parse_access_token_file(path) -> str:
        with open(path, 'r') as file:
            data = json.load(file)
            return data['access_token']


class StaticCredential(CredentialProvider):

    def __init__(self, access_token=None):
        self.access_token = access_token

    def get_access_token(self) -> str:
        if not self.access_token:
            raise CredentialUnavailableError(f'Access Token not set')
        return self.access_token


class DefaultCredentialsProvider(CredentialProvider):

    def __init__(self, access_token=None):
        self.credentials = [
            StaticCredential(access_token),
            EnvironmentCredential(),
            TokenFileCredential(),
        ]

    def get_access_token(self) -> str:
        for credential in self.credentials:
            try:
                access_token = credential.get_access_token()
                logger.info('%s acquired an access token from %s',
                            self.__class__.__name__, credential.__class__.__name__)
                return access_token
            except CredentialUnavailableError:
                logger.info('%s - %s is unavailable', self.__class__.__name__, credential.__class__.__name__)
            except Exception as e:
                logger.info('%s.get_access_token() failed: %s raised unexpected error "%s"', self.__class__.__name__,
                            credential.__class__.__name__, e, exc_info=logger.isEnabledFor(logging.DEBUG))

        message = f'{self.__class__.__name__} failed to retrieve an access token'
        logger.warning(message)
        raise PlanqkClientError(message)
