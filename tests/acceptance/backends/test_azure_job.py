import os

from azure.identity import ClientSecretCredential
from azure.quantum import Workspace
from azure.quantum.qiskit import AzureQuantumProvider
from qiskit.result.models import ExperimentResultData

from tests.acceptance.backends.base_job_test import BaseJobTest
from tests.acceptance.backends.test_braket_backend import BACKEND_ID_AZURE_IONQ_HARMONY, BACKEND_ID_AZURE_IONQ_SIM
from tests.utils import get_sample_circuit, is_valid_uuid, transform_decimal_to_bitsrings

AZURE_NAME_IONQ_HARMONY= "ionq.qpu"
AZURE_NAME_IONQ_SIM = "ionq.simulator"

class AzureJobTestSuite(BaseJobTest):

    def setUp(self):
        super().setUp()

        AZ_TENANT_ID = os.environ.get('AZ_TENANT_ID')
        AZ_CLIENT_ID = os.environ.get('AZ_CLIENT_ID')
        AZ_CLIENT_SECRET = os.environ.get('AZ_CLIENT_SECRET')
        AZ_QUANTUM_RESOURCE_ID = os.environ.get('AZ_QUANTUM_RESOURCE_ID')
        AZ_REGION = os.environ.get('AZ_REGION')

        PLANQK_QUANTUM_BASE_URL = os.environ.get('PLANQK_QUANTUM_BASE_URL')
        PLANQK_ACCESS_TOKEN = os.environ.get('PLANQK_ACCESS_TOKEN')

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
        self.azure_provider = AzureQuantumProvider(
            workspace=workspace
        )

    def get_provider(self):
        return self.azure_provider

    def get_provider_id(self):
        return "AZURE"

    def is_simulator(self, backend_id):
        if backend_id == BACKEND_ID_AZURE_IONQ_SIM:
            return True
        return False


    def test_should_run_job_azure_ionq_harmony(self):
        job_id = self.test_should_run_job(BACKEND_ID_AZURE_IONQ_HARMONY, 1)
        is_valid_uuid(job_id)

    def test_should_run_job_azure_ionq_sim(self):
        job_id = self.test_should_run_job(BACKEND_ID_AZURE_IONQ_SIM, 1)
        is_valid_uuid(job_id)

    def test_should_retrieve_job_azure_ionq_harmony(self):
        job_id = ""
        self.test_should_retrieve_job(AZURE_NAME_IONQ_HARMONY, BACKEND_ID_AZURE_IONQ_HARMONY, job_id, 1)

    def test_should_retrieve_job_azure_ionq_sim(self):
        job_id = "d2f92b66-d83f-4110-98ac-a35d0210b285"
        self.test_should_retrieve_job(AZURE_NAME_IONQ_SIM, BACKEND_ID_AZURE_IONQ_SIM, job_id, 1)

    def assert_experimental_result_data(self, result: ExperimentResultData, exp_result: ExperimentResultData,
                                        is_random_result=False):
        if is_random_result:
            self.assertTrue(result.counts == {'111': 1} or result.counts == {'000': 1})
        else:
            num_qubits = len(self.input_circuit.qubits)
            exp_counts = transform_decimal_to_bitsrings(result.counts, num_qubits)
            self.assertTrue(result.counts, exp_counts)

    def test_should_retrieve_job_result_ionq_harmony(self):
        job_id = "d2f92b66-d83f-4110-98ac-a35d0210b285"
        self.test_should_retrieve_job_result(AZURE_NAME_IONQ_HARMONY, BACKEND_ID_AZURE_IONQ_HARMONY, job_id)

    def test_should_retrieve_job_result_ionq_sim(self):
        job_id = "d2f92b66-d83f-4110-98ac-a35d0210b285"
        self.test_should_retrieve_job_result(AZURE_NAME_IONQ_SIM, BACKEND_ID_AZURE_IONQ_SIM, job_id)

