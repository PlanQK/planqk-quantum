import logging
import os
import unittest
from uuid import UUID

from dotenv import load_dotenv

from planqk.qiskit.provider import PlanqkQuantumProvider
from tests.acceptance.backends.backends_list import SUPPORTED_BACKENDS

logging.basicConfig(level=logging.DEBUG)


def is_valid_uuid(uuid_to_test):
    try:
        UUID(str(uuid_to_test))
    except ValueError:
        return False
    return True


class AllBackendsTestSuite(unittest.TestCase):

    def setUp(self):
        load_dotenv()

        PLANQK_QUANTUM_BASE_URL = os.environ.get('PLANQK_QUANTUM_BASE_URL')
        PLANQK_ACCESS_TOKEN = os.environ.get('PLANQK_ACCESS_TOKEN')

        self.assertIsNotNone(PLANQK_QUANTUM_BASE_URL,
                             "Env variable PLANQK_QUANTUM_BASE_URL (PlanQK quantum base url) not set")
        self.assertIsNotNone(PLANQK_ACCESS_TOKEN,
                             "Env variable PLANQK_ACCESS_TOKEN (PlanQK API access token) not set")

        self.planqk_provider = PlanqkQuantumProvider(PLANQK_ACCESS_TOKEN)

    def test_should_list_all_backends(self):
        backend_names = []
        for backend in self.planqk_provider.backends():
            backend_names.append(backend)

        assert set(backend_names) == set(SUPPORTED_BACKENDS)


if __name__ == '__main__':
    unittest.main()
