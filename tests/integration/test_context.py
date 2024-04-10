import os
import tempfile
import unittest.mock

from planqk.context import ContextResolver
from planqk.qiskit import PlanqkQuantumProvider
from planqk.qiskit.client.client import _PlanqkClient


def _create_context_env_file():
    json_value = """
    {
        "context": {
            "id": "c557000f-f2b1-4505-8172-dac7960caf16",
            "displayName": "Test Org",
            "isOrganization": true
        }
    }
    """
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fp:
        fp.write(json_value.encode("utf-8"))
        os.environ["PLANQK_CONFIG_FILE_PATH"] = os.path.abspath(fp.name)


class ContextResolverTestSuite(unittest.TestCase):

    def tearDown(self):
        if "PLANQK_CONFIG_FILE_PATH" in os.environ:
            del os.environ["PLANQK_CONFIG_FILE_PATH"]
        if "PLANQK_ORGANIZATION_ID" in os.environ:
            del os.environ["PLANQK_ORGANIZATION_ID"]

    def test_should_get_organization_id_from_context_when_env_var_set(self):
        json_value = """
        {
            "context": {
                "id": "c557000f-f2b1-4505-8172-dac7960caf16",
                "displayName": "Test User",
                "isOrganization": false
            }
        }
        """
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fp:
            fp.write(json_value.encode("utf-8"))
            os.environ["PLANQK_CONFIG_FILE_PATH"] = os.path.abspath(fp.name)

        os.environ["PLANQK_ORGANIZATION_ID"] = "c557000f-f2b1-4505-8172-dac7960caf15"

        context_resolver = ContextResolver()
        context = context_resolver.get_context()

        self.assertIsNotNone(context)
        self.assertEqual(context.is_organization, False)
        self.assertEqual(context.get_organization_id(), "c557000f-f2b1-4505-8172-dac7960caf15")

    def test_should_get_organization_id_from_context(self):
        _create_context_env_file()

        context_resolver = ContextResolver()
        context = context_resolver.get_context()

        self.assertIsNotNone(context)
        self.assertEqual(context.is_organization, True)
        self.assertEqual(context.get_organization_id(), "c557000f-f2b1-4505-8172-dac7960caf16")

    def test_should_retrieve_context_from_config(self):
        json_value = """
        {
            "context": {
                "id": "c557000f-f2b1-4505-8172-dac7960caf16",
                "displayName": "Test User",
                "isOrganization": false
            }
        }
        """
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fp:
            fp.write(json_value.encode("utf-8"))
            os.environ["PLANQK_CONFIG_FILE_PATH"] = os.path.abspath(fp.name)

        context_resolver = ContextResolver()
        context = context_resolver.get_context()

        self.assertIsNotNone(context)
        self.assertEqual(context.id, "c557000f-f2b1-4505-8172-dac7960caf16")
        self.assertEqual(context.display_name, "Test User")
        self.assertEqual(context.is_organization, False)
        self.assertIsNone(context.get_organization_id())

    def test_should_return_none_when_file_not_present(self):
        os.environ["PLANQK_CONFIG_FILE_PATH"] = "/var/folders/c6/32xv5kh16p19yf8yz7bl294h0000gn/T/tmp8iqmj5ji.json"

        context_resolver = ContextResolver()
        context = context_resolver.get_context()

        self.assertIsNone(context)

    def test_should_return_none_when_file_is_empty(self):
        json_value = "{}"
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fp:
            fp.write(json_value.encode("utf-8"))
            os.environ["PLANQK_CONFIG_FILE_PATH"] = os.path.abspath(fp.name)

        context_resolver = ContextResolver()
        context = context_resolver.get_context()

        self.assertIsNone(context)

    def test_should_use_user_provided_org_id(self):
        _create_context_env_file()
        access_token = "user_access_token"
        user_org_id = "user_org_id"
        PlanqkQuantumProvider(access_token, user_org_id)
        self.assertEqual(_PlanqkClient._get_default_headers()["x-organizationid"], user_org_id)
