from qiskit.result.models import ExperimentResultData

from planqk.qiskit.client.backend_dtos import PROVIDER
from tests.acceptance.backends.azure_test_utils import init_azure_provider, AZURE_NAME_IONQ_SIM, \
    BACKEND_ID_AZURE_IONQ_SIM
from tests.acceptance.backends.base_job_test import BaseJobTest
from tests.utils import is_valid_uuid, transform_decimal_to_bitsrings
from qiskit.result.models import ExperimentResultData

from planqk.qiskit.client.backend_dtos import PROVIDER
from tests.acceptance.backends.azure_test_utils import init_azure_provider, AZURE_NAME_IONQ_SIM, \
    BACKEND_ID_AZURE_IONQ_SIM
from tests.acceptance.backends.base_job_test import BaseJobTest
from tests.utils import is_valid_uuid


class AzureIonqSimJobTests(BaseJobTest):

    def setUp(self):
        super().setUp()

        self.azure_provider = init_azure_provider()

    def get_provider(self):
        return self.azure_provider

    def get_provider_id(self):
        return PROVIDER.AZURE.name

    def get_backend_id(self) -> str:
        return BACKEND_ID_AZURE_IONQ_SIM

    def get_provider_backend_name(self) -> str:
        return AZURE_NAME_IONQ_SIM

    def get_test_shots(self) -> int:
        return 1

    def is_simulator(self) -> bool:
        return True

    def get_provider_job_id(self, job_id: str) -> str:
        return job_id

    def is_valid_job_id(self, job_id: str) -> bool:
        return is_valid_uuid(job_id)

    def assert_experimental_result_data(self, result: ExperimentResultData, exp_result: ExperimentResultData):
        num_qubits = len(self.input_circuit.qubits)
        exp_counts = transform_decimal_to_bitsrings(exp_result.counts, num_qubits)
        # Ionq simulator returns probabilities, hence, Azure SDK generates random memory values -> memory not asserted
        self.assertEqual(result.counts, exp_counts)
        # But it is checked if a memory is returned as PlanQK generates random memory values for simulators
        self.assertTrue(len(result.memory) == 1)

    # Tests

    def test_should_get_backend(self):
        self.should_get_backend()

    def test_should_run_job(self):
        self.should_run_job()

    def test_should_retrieve_job(self):
        self.should_retrieve_job()

    def test_should_retrieve_job_result(self):
        self.should_retrieve_job_result()

    def test_should_cancel_job(self):
        # Skip this test as Azure Ionq simulator does not support cancelling jobs
        pass

    def test_should_retrieve_job_status(self):
        self.should_retrieve_job_status()