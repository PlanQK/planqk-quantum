from tests.acceptance.backends.backends_list import BACKEND_ID_IBM_NAIROBI
from tests.acceptance.backends.ibm_primitive_base_test import IbmPrimitiveBaseTest
from tests.acceptance.backends.ibm_test_utils import IBM_NAIROBI_NAME


class IbmPrimitiveNairobiBackendTests(IbmPrimitiveBaseTest):

    def get_backend_id(self) -> str:
        return BACKEND_ID_IBM_NAIROBI

    def get_provider_backend_name(self) -> str:
        return IBM_NAIROBI_NAME

    def get_test_shots(self) -> int:
        return 10

    def is_simulator(self) -> bool:
        return False

    def supports_memory_result(self) -> bool:
        return True

    # Tests

    def test_should_get_backend(self):
        self.should_get_backend()

    def test_should_transpile_circuit(self):
        self.should_transpile_circuit()

    def test_should_not_run_job_with_classic_provider(self):
        self.should_not_run_job_with_classic_provider()

    def test_should_run_job(self):
        self.should_run_job()

    def test_should_run_multiple_jobs_in_session(self):
        self.should_run_multiple_jobs_in_session()

    def test_should_retrieve_job(self):
        self.should_retrieve_job()

    def test_should_retrieve_job_result(self):
        self.should_retrieve_job_result()

    def test_should_retrieve_estimator_job_result(self):
        pass

    def test_should_cancel_job(self):
        self.should_cancel_job()

    def test_should_retrieve_job_status(self):
        self.should_retrieve_job_status()
