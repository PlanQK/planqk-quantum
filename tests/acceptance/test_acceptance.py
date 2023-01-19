import logging
import os
import sys
import unittest
from io import StringIO
from uuid import UUID

from azure.identity import ClientSecretCredential
from azure.quantum import Workspace
from azure.quantum.qiskit import AzureQuantumProvider
from busypie import wait
from qiskit.providers import JobStatus
from qiskit.tools import job_monitor

from planqk.qiskit import PlanqkQuantumProvider
from tests.utils import get_sample_circuit, to_dict

logging.basicConfig(level=logging.DEBUG)

AZ_TENANT_ID = os.environ.get('AZ_TENANT_ID')
AZ_CLIENT_ID = os.environ.get('AZ_CLIENT_ID')
AZ_CLIENT_SECRET = os.environ.get('AZ_CLIENT_SECRET')
AZ_QUANTUM_RESOURCE_ID = os.environ.get('AZ_QUANTUM_RESOURCE_ID')
AZ_REGION = os.environ.get('AZ_REGION')

PLANQK_QUANTUM_BASE_URL = os.environ.get('PLANQK_QUANTUM_BASE_URL')
PLANQK_ACCESS_TOKEN = os.environ.get('PLANQK_ACCESS_TOKEN')

SUPPORTED_BACKENDS = {"ionq.qpu", "ionq.simulator"}


def is_valid_uuid(uuid_to_test):
    try:
        UUID(str(uuid_to_test))
    except ValueError:
        return False
    return True


class AcceptanceTestSuite(unittest.TestCase):

    def setUp(self):

        self.assertIsNotNone(AZ_TENANT_ID, "Env variable AZ_TENANT_ID (Azure tenant id) not set")
        self.assertIsNotNone(AZ_CLIENT_ID, "Env variable AZ_CLIENT_ID (Azure client id) not set")
        self.assertIsNotNone(AZ_CLIENT_SECRET, "Env variable AZ_CLIENT_SECRET (Azure client secret) not set")
        self.assertIsNotNone(AZ_QUANTUM_RESOURCE_ID, "Env variable AZ_QUANTUM_RESOURCE_ID "
                                                     "(Azure quantum resource id) not set")
        self.assertIsNotNone(AZ_REGION, "Env variable AZ_REGION (Azure region name) not set")
        self.assertIsNotNone(PLANQK_QUANTUM_BASE_URL,
                             "Env variable PLANQK_QUANTUM_BASE_URL (PlanQK quantum base url) not set")
        self.assertIsNotNone(PLANQK_ACCESS_TOKEN,
                             "Env variable PLANQK_ACCESS_TOKEN (PlanQK API access token) not set")

        credential = ClientSecretCredential(tenant_id=AZ_TENANT_ID,
                                            client_id=AZ_CLIENT_ID,
                                            client_secret=AZ_CLIENT_SECRET)

        workspace = Workspace(
            # Format must match
            resource_id=AZ_QUANTUM_RESOURCE_ID,
            location=AZ_REGION,
            credential=credential
        )
        provider = AzureQuantumProvider(
            workspace=workspace
        )
        self.azure_provider = provider
        self.planqk_provider = PlanqkQuantumProvider(PLANQK_ACCESS_TOKEN)

        # Ensure to see the diff of large objects
        self.maxDiff = None

    def test_should_list_all_backends(self):
        # Get backend names via AzureProvider
        exp_backend_names = []
        for backend in self.azure_provider.backends():
            exp_backend_names.append(backend.name())

        # Get backend names via PlanqkProvider
        backend_names = []
        for backend in self.planqk_provider.backends():
            backend_names.append(backend.name())

        assert set(backend_names) == set(exp_backend_names).intersection(SUPPORTED_BACKENDS)

    def test_should_get_backend(self):
        # Get backend via AzureProvider
        exp_backend = self.azure_provider.get_backend("ionq.qpu")

        # Get backend via PlanqkProvider
        backend = self.planqk_provider.get_backend("ionq.qpu")

        assert backend.name() == exp_backend.name()
        assert backend.backend_name == exp_backend.backend_name
        assert set(backend.backend_names) == set(exp_backend.backend_names)
        assert backend.configuration() == exp_backend.configuration()
        assert backend.options.shots == exp_backend.options.shots
        assert backend.status() == exp_backend.status()
        assert backend.version == exp_backend.version

    def test_should_run_job(self):

        sim_backend = self.planqk_provider.get_backend("ionq.simulator")
        circuit = get_sample_circuit(sim_backend)
        job = sim_backend.run(circuit, shots=1)
        job_id = job.id()

        assert is_valid_uuid(job_id)

    def test_should_retrieve_job(self):
        # Given: create job
        sim_backend = self.planqk_provider.get_backend("ionq.simulator")
        circuit = get_sample_circuit(sim_backend)
        created_job = sim_backend.run(circuit, shots=1)

        # When

        # Get job via Azure
        azure_backend = self.azure_provider.get_backend("ionq.simulator")
        exp_job = azure_backend.retrieve_job(created_job.id())

        # Get job via PlanQK
        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(created_job.id())

        # Then
        assert exp_job.id() == job.id()
        assert exp_job.version == job.version
        assert exp_job.metadata == job.metadata

    def test_should_retrieve_job_via_provider(self):
        # Given: create job
        sim_backend = self.planqk_provider.get_backend("ionq.simulator")
        circuit = get_sample_circuit(sim_backend)
        created_job = sim_backend.run(circuit, shots=1)

        # When

        # Get job via Azure
        exp_job = self.azure_provider.get_job(created_job.id())

        # Get job via PlanQK
        job = self.planqk_provider.get_job(created_job.id())

        # Then
        assert exp_job.id() == job.id()
        assert exp_job.version == job.version
        assert exp_job.metadata == job.metadata

    def test_should_retrieve_job_result(self):
        # Given: create job
        sim_backend = self.planqk_provider.get_backend("ionq.simulator")
        circuit = get_sample_circuit(sim_backend)
        created_job = sim_backend.run(circuit, shots=1)

        # When

        # Get job result via Azure
        azure_backend = self.azure_provider.get_backend("ionq.simulator")
        azure_job = azure_backend.retrieve_job(created_job.id())
        azure_result = azure_job.result()
        exp_job_result_dict = to_dict(azure_result)

        # Get job via PlanQK
        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(azure_job.id())
        job_result_dict = to_dict(job.result())

        # job_result/results[0]/counts may contain either the key 000 or 111 -> the field is removed to assert dicts
        exp_job_result_dict.get("results")[0].get('data').pop('counts')
        counts = job_result_dict.get("results")[0].get('data').pop('counts')
        self.assertTrue(counts.get("111") == 1 or counts.get("000") == 1)

        self.assertDictEqual(exp_job_result_dict, job_result_dict)

    def test_should_retrieve_job_status(self):
        sim_backend = self.planqk_provider.get_backend("ionq.simulator")
        circuit = get_sample_circuit(sim_backend)
        created_job = sim_backend.run(circuit, shots=1)

        # Get job status via PlanQK
        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(created_job.id())
        job_status = job.status()

        # Then
        self.assertIn(job_status.name, [JobStatus.QUEUED.name, JobStatus.DONE.name])

    def test_should_monitor_job(self):
        sim_backend = self.planqk_provider.get_backend("ionq.simulator")
        circuit = get_sample_circuit(sim_backend)
        created_job = sim_backend.run(circuit, shots=1)

        # Get job status via PlanQK
        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(created_job.id())
        sys.stdout = planqk_stdout = StringIO()

        job_monitor(job, output=planqk_stdout)

        console_output = planqk_stdout.getvalue()

        self.assertIn('Job Status: job has successfully run', console_output)

    def test_should_cancel_job(self):
        sim_backend = self.planqk_provider.get_backend("ionq.simulator")
        circuit = get_sample_circuit(sim_backend)
        planqk_job = sim_backend.run(circuit, shots=1)
        planqk_job.cancel()

        def assert_job_cancelled():
            job_status = planqk_job.status()
            assert job_status.name == JobStatus.CANCELLED.name

        wait().until_asserted(assert_job_cancelled)


if __name__ == '__main__':
    unittest.main()
