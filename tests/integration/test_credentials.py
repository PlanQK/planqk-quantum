import os
import unittest.mock
from planqk.qiskit import PlanqkQuantumProvider


class CredentialsTestSuite(unittest.TestCase):

    def setUp(self):
        if "SERVICE_EXECUTION_TOKEN" in os.environ:
            del os.environ["SERVICE_EXECUTION_TOKEN"]


    def test_should_use_user_provided_token(self):
        access_token = "user_access_token"
        planqk_provider = PlanqkQuantumProvider(
            access_token)
        self.assertEqual(planqk_provider.get_access_token(), access_token)

    def test_env_provided_token_priority(self):
        access_token = "service_access_token"
        os.environ["SERVICE_EXECUTION_TOKEN"] = access_token

        planqk_provider = PlanqkQuantumProvider(
            "user_access_token")
        # env set token must have priority to access token set by user
        self.assertEqual(access_token, planqk_provider.get_access_token())
