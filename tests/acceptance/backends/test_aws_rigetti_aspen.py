from qiskit_braket_provider import AWSBraketProvider

from tests.acceptance.backends.base_job_test import BaseJobTest
from tests.acceptance.backends.braket_test_utils import is_valid_aws_arn, transform_job_id_to_arn, \
    BRAKET_NAME_IONQ_HARMONY, BRAKET_NAME_RIGETTI_ASPEN
from tests.acceptance.backends.test_braket_backend import BACKEND_ID_AWS_IONQ_HARMONY, BACKEND_ID_AWS_RIGETTI_ASPEN


class AwsRigettiAspenJobTests(BaseJobTest):

    def setUp(self):
        super().setUp()
        self.braket_provider = AWSBraketProvider()

    def get_provider(self):
        return self.braket_provider

    def get_provider_id(self):
        return "AWS"

    def get_backend_id(self) -> str:
        return BACKEND_ID_AWS_RIGETTI_ASPEN

    def get_provider_backend_name(self) -> str:
        return BRAKET_NAME_RIGETTI_ASPEN

    def get_test_shots(self) -> int:
        return 1

    def is_simulator(self) -> bool:
        return False

    def get_provider_job_id(self, job_id: str) -> str:
        return transform_job_id_to_arn(job_id)

    def is_valid_job_id(self, job_id: str) -> bool:
        return is_valid_aws_arn(job_id)

    #Tests

    def test_should_get_backend(self):
        self.should_get_backend()

    def test_should_get_backend(self):
        self.should_get_backend()

    def test_should_run_job(self):
        self.should_run_job()

    def test_should_retrieve_job(self):
        self.should_retrieve_job()

    def test_should_retrieve_job_result(self):
        self.should_retrieve_job_result()

    def test_should_cancel_job(self):
        self.should_cancel_job()

    def test_should_retrieve_job_status(self):
        self.should_retrieve_job_status()
