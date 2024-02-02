import unittest

from planqk.qiskit.options import OptionsV2
from tests.unit.planqk.backends import MockBackend


class OptionsTestSuite(unittest.TestCase):

    def test_options_patch(self):
        options = OptionsV2(foo="bar")

        self.assertEqual(options["foo"], "bar")
        self.assertEqual(options.data, ["foo"])

        options["foo"] = "baz"
        self.assertEqual(options["foo"], "baz")

        options.update_options(foo="qux")
        self.assertEqual(options["foo"], "qux")

    def test_set_backend_options(self):
        backend = MockBackend(foo="baz")

        self.assertEqual(backend.options["foo"], "baz")
