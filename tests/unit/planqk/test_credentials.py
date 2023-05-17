import unittest

from planqk.credentials import ConfigFileCredential


class CredentialProviderTestSuite(unittest.TestCase):

    def test_should_get_access_token_from_config_file(self):
        provider = ConfigFileCredential()
        access_token = provider.get_access_token()
        self.assertIsNotNone(access_token)
