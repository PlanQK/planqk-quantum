import os
import platform
import unittest

from planqk.credentials import ConfigFileCredential


def get_config_file_path():
    if platform.system() == 'Windows':
        config_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'planqk')
    else:
        config_dir = os.path.join(os.path.expanduser('~'), '.config', 'planqk')
    return os.path.join(config_dir, 'config.json')


class CredentialsTestSuite(unittest.TestCase):

    def test_should_get_access_token_from_config_file(self):
        # check if config file exists, if not create it and write mock data
        config_file_path = get_config_file_path()
        if not os.path.isfile(config_file_path):
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
            with open(config_file_path, 'w') as file:
                file.write('{"auth": {"type": "API_KEY", "value": "plqk_test"}}')

        config_file_provider = ConfigFileCredential()
        access_token = config_file_provider.get_access_token()

        self.assertIsNotNone(access_token)
        self.assertIs(type(access_token), str)
        self.assertIs(len(access_token) > 0, True)
