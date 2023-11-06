import pytest
from qiskit import QuantumCircuit
from qiskit_braket_provider import AWSBraketProvider

from planqk.qiskit.client.backend_dtos import PROVIDER
from tests.acceptance.backends.backends_list import BACKEND_ID_AWS_RIGETTI_ASPEN
from tests.acceptance.backends.base_test import BaseTest
from tests.acceptance.backends.braket_test_utils import is_valid_aws_arn, transform_job_id_to_arn, \
    BRAKET_NAME_RIGETTI_ASPEN
from tests.utils import get_width_sample_circuit


@pytest.mark.aws
class AwsRigettiAspenTests(BaseTest):

    def setUp(self):
        super().setUp()
        self.braket_provider = AWSBraketProvider()

    def get_provider(self):
        return self.braket_provider

    def get_provider_id(self):
        return PROVIDER.AWS.name

    def get_backend_id(self) -> str:
        return BACKEND_ID_AWS_RIGETTI_ASPEN

    def get_provider_backend_name(self) -> str:
        return BRAKET_NAME_RIGETTI_ASPEN

    def get_test_shots(self) -> int:
        # Rigetti has min shots of 10
        return 10

    def is_simulator(self) -> bool:
        return False

    def supports_memory_result(self) -> bool:
        return True

    def get_provider_job_id(self, job_id: str) -> str:
        return transform_job_id_to_arn(job_id)

    def is_valid_job_id(self, job_id: str) -> bool:
        return is_valid_aws_arn(job_id)

    def get_input_circuit(self) -> QuantumCircuit:
        return get_width_sample_circuit(79)

    # Tests

    def test_should_get_backend(self):
        self.should_get_backend()

    def test_should_transpile_circuit(self):
        self.should_transpile_circuit()

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
