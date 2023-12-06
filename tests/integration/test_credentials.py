import os
import unittest.mock

from planqk.context import get_config_file_path
from planqk.qiskit import PlanqkQuantumProvider


class CredentialsTestSuite(unittest.TestCase):

    def setUp(self):
        if "SERVICE_EXECUTION_TOKEN" in os.environ:
            del os.environ["SERVICE_EXECUTION_TOKEN"]

    def test_should_use_user_provided_token(self):
        access_token = "user_access_token"
        planqk_provider = PlanqkQuantumProvider(access_token)
        self.assertEqual(planqk_provider.get_access_token(), access_token)

    def test_env_provided_token_priority(self):
        access_token = "service_access_token"
        os.environ["SERVICE_EXECUTION_TOKEN"] = access_token

        planqk_provider = PlanqkQuantumProvider("user_access_token")

        # env set token must have priority to access token set by user
        self.assertEqual("user_access_token", planqk_provider.get_access_token())

    def test_should_get_access_token_from_config_file(self):
        # check if config file exists, if not create it and write mock data
        config_file_path = get_config_file_path()
        if not os.path.isfile(config_file_path):
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
            with open(config_file_path, 'w') as file:
                file.write("""{
                    "auth": {
                        "type": "API_KEY", 
                        "value": "plqk_test"
                    }
                }
                """)

        planqk_provider = PlanqkQuantumProvider()

        access_token = planqk_provider.get_access_token()
        self.assertIsNotNone(access_token)
        self.assertIs(type(access_token), str)
        self.assertIs(len(access_token) > 0, True)
