from qiskit_braket_provider import AWSBraketProvider

from planqk.qiskit.client.backend_dtos import PROVIDER
from tests.acceptance.backends.base_test import BaseTest
from tests.acceptance.backends.braket_test_utils import is_valid_aws_arn, transform_job_id_to_arn, BRAKET_NAME_SV1
from tests.acceptance.backends.backends_list import BACKEND_ID_AWS_SV1


class AwsSv1Tests(BaseTest):

    def setUp(self):
        super().setUp()
        self.braket_provider = AWSBraketProvider()

    def get_provider(self):
        return self.braket_provider

    def get_provider_id(self):
        return PROVIDER.AWS.name

    def get_backend_id(self) -> str:
        return BACKEND_ID_AWS_SV1

    def get_provider_backend_name(self) -> str:
        return BRAKET_NAME_SV1

    def get_test_shots(self) -> int:
        return 1

    def is_simulator(self) -> bool:
        return True

    def get_provider_job_id(self, job_id: str) -> str:
        return transform_job_id_to_arn(job_id)

    def is_valid_job_id(self, job_id: str) -> bool:
        return is_valid_aws_arn(job_id)

    #Tests

    def test_should_get_backend(self):
        self.should_get_backend()

    def test_should_transpile_circuit(self):
        # For simulators transpilation is not required
        pass

    def test_should_run_job(self):
        self.should_run_job()

    def test_should_retrieve_job(self):
        self.should_retrieve_job()

    def test_should_retrieve_job_result(self):
        self.should_retrieve_job_result()

    def test_should_cancel_job(self):
        # Cannot be tested as simulator jobs may complete instantly
        pass

    def test_should_retrieve_job_status(self):
        self.should_retrieve_job_status()


