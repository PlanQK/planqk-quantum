import os
import tempfile
import unittest.mock

from planqk.qiskit import PlanqkQuantumProvider
from planqk.qiskit.client.client import _PlanqkClient


class CredentialsTestSuite(unittest.TestCase):

    def setUp(self):
        if "SERVICE_EXECUTION_TOKEN" in os.environ:
            del os.environ["SERVICE_EXECUTION_TOKEN"]

    def tearDown(self):
        if "PLANQK_CONFIG_FILE_PATH" in os.environ:
            del os.environ["PLANQK_CONFIG_FILE_PATH"]

    def test_should_use_user_provided_token(self):
        access_token = "user_access_token"
        planqk_provider = PlanqkQuantumProvider(access_token)
        self.assertEqual(access_token, _PlanqkClient.get_credentials().get_access_token())

    def test_env_provided_token_priority(self):
        access_token = "service_access_token"
        os.environ["SERVICE_EXECUTION_TOKEN"] = access_token

        planqk_provider = PlanqkQuantumProvider("user_access_token")

        # env set token must have priority to access token set by user
        self.assertEqual("user_access_token", _PlanqkClient.get_credentials().get_access_token())

    def test_should_get_access_token_from_config_file(self):
        json_value = """
        {
            "auth": {
                "type": "API_KEY", 
                "value": "plqk_test"
            }
        }
        """
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fp:
            fp.write(json_value.encode("utf-8"))
            os.environ["PLANQK_CONFIG_FILE_PATH"] = os.path.abspath(fp.name)

        planqk_provider = PlanqkQuantumProvider()

        access_token = _PlanqkClient.get_credentials().get_access_token()
        self.assertIsNotNone(access_token)
        self.assertEqual(access_token, "plqk_test")
