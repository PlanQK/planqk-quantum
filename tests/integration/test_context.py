import os
import tempfile
import unittest.mock

from planqk.context import ContextResolver


class ContextResolverTestSuite(unittest.TestCase):

    def tearDown(self):
        if "PLANQK_CONFIG_FILE_PATH" in os.environ:
            del os.environ["PLANQK_CONFIG_FILE_PATH"]

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
        self.assertEqual(context.displayName, "Test User")
        self.assertEqual(context.isOrganization, False)

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
