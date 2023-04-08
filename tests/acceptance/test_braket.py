import logging
import os
import sys
import unittest
from io import StringIO
from uuid import UUID

from planqk.qiskit import PlanqkQuantumProvider
from tests.acceptance.test_acceptance import is_valid_uuid
from tests.utils import get_sample_circuit, to_dict
from qiskit_braket_provider import AWSBraketProvider

logging.basicConfig(level=logging.DEBUG)

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('PLANQK_ACCESS_TOKEN')

PLANQK_QUANTUM_BASE_URL = os.environ.get('PLANQK_QUANTUM_BASE_URL')
PLANQK_ACCESS_TOKEN = os.environ.get('PLANQK_ACCESS_TOKEN')

SUPPORTED_BACKENDS = {"ionq.qpu", "ionq.simulator"}

class AwsBraketTestSuite(unittest.TestCase):

    def setUp(self):
        #self.assertIsNotNone(AWS_ACCESS_KEY, "Env variable AWS_ACCESS_KEY (Azure tenant id) not set")
        #self.assertIsNotNone(AWS_SECRET_ACCESS_KEY, "Env variable AWS_SECRET_ACCESS_KEY (Azure client id) not set")

        self.assertIsNotNone(PLANQK_QUANTUM_BASE_URL,
                             "Env variable PLANQK_QUANTUM_BASE_URL (PlanQK quantum base url) not set")
        self.assertIsNotNone(PLANQK_ACCESS_TOKEN,
                             "Env variable PLANQK_ACCESS_TOKEN (PlanQK API access token) not set")

        self.braket_provider = AWSBraketProvider()
        self.planqk_provider = PlanqkQuantumProvider(PLANQK_ACCESS_TOKEN)

        # Ensure to see the diff of large objects
        self.maxDiff = None

    def test_should_list_all_backends(self):
        # Get backend names via AWS Braket
        exp_backend_names = []
        exp_backends = self.braket_provider.backends()
        for backend in exp_backends:
            exp_backend_names.append(backend.name)

        # Get backend names via PlanqkProvider
        backend_names = []
        backends = self.planqk_provider.backends()
        for backend in backends:
            backend_names.append(backend.name)

        assert set(backend_names) == set(exp_backend_names).intersection(SUPPORTED_BACKENDS)

    def test_should_get_backend(self):
        pass

    def test_should_run_job(self):
        sim_backend = self.planqk_provider.get_backend("TN1")
        circuit = get_sample_circuit(sim_backend)
        job = sim_backend.run(circuit, shots=1)
        job_id = job.id()

        assert is_valid_uuid(job_id)