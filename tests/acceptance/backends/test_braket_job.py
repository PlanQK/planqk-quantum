from qiskit_braket_provider import AWSBraketProvider

from tests.acceptance.backends.base_job_test import BaseJobTest
from tests.acceptance.backends.braket_test_utils import is_valid_aws_arn
from tests.acceptance.backends.test_braket_backend import BACKEND_ID_AWS_IONQ_ARIA, BACKEND_ID_AWS_DM1, \
    BACKEND_ID_AWS_IONQ_HARMONY, \
    BACKEND_ID_AWS_RIGETTI_ASPEN, BACKEND_ID_AWS_SV1, BACKEND_ID_AZURE_IONQ_HARMONY, BACKEND_ID_AZURE_IONQ_SIM, \
    BACKEND_ID_AWS_OQC_LUCY
from tests.utils import get_sample_circuit, is_valid_uuid

BRAKET_NAME_SV1 = "SV1"
BRAKET_NAME_DM1 = "dm1"
BRAKET_NAME_IONQ_ARIA = "Aria 1"
BRAKET_NAME_IONQ_HARMONY = "Harmony"
BRAKET_NAME_RIGETTI_ASPEN = "Aspen-11"
BRAKET_NAME_OQC_LUCY = "Lucy"


class BraketJobTestSuite(BaseJobTest):

    def setUp(self):
        super().setUp()
        self.braket_provider = AWSBraketProvider()

    def get_provider(self):
        return self.braket_provider

    def get_provider_id(self):
        return "AWS"

    def is_simulator(self, backend_id):
        if backend_id in [BACKEND_ID_AWS_SV1, BACKEND_ID_AWS_DM1]:
            return True
        return False

    def get_provider_job_id(self, job_id: str) -> str:
        return job_id.replace("_", "/")

    def test_should_run_job_sv1(self):
        job = self.test_should_run_job(BACKEND_ID_AWS_SV1, 1)
        is_valid_aws_arn(job.id)

    def test_should_run_job_dm1(self):
        job = self.test_should_run_job(BACKEND_ID_AWS_DM1, 1)
        is_valid_aws_arn(job.id)

    def test_should_run_job_ionq_aria(self):
        job = self.test_should_run_job(BACKEND_ID_AWS_IONQ_ARIA, 1)
        is_valid_aws_arn(job.id)

    def test_should_run_job_ionq_harmony(self):
        job = self.test_should_run_job(BACKEND_ID_AWS_IONQ_HARMONY, 1)
        is_valid_aws_arn(job.id)

    def test_should_run_job_rigetti(self):
        job = self.test_should_run_job(BACKEND_ID_AWS_RIGETTI_ASPEN, 10)
        is_valid_aws_arn(job.id)

    def test_should_run_job_oqc_lucy(self):
        job = self.test_should_run_job(BACKEND_ID_AWS_OQC_LUCY, 10)
        is_valid_aws_arn(job.id)

    def test_should_retrieve_job_sv1(self):
        job_id = "arn:backends:braket:us-east-1:750565748698:quantum-task_f7c4504e-265f-4f2b-943d-3071eadd1824"
        self.test_should_retrieve_job(BRAKET_NAME_SV1, BACKEND_ID_AWS_SV1, job_id, 1)

    def test_should_retrieve_job_dm1(self):
        job_id = "arn:backends:braket:us-east-1:750565748698:quantum-task_3c37a335-84a8-49a2-b7ca-3e2aafed8d39"
        self.test_should_retrieve_job(BRAKET_NAME_DM1, BACKEND_ID_AWS_DM1, job_id, 1)

    def test_should_retrieve_job_ionq_aria(self):
        job_id = "arn:backends:braket:us-east-1:750565748698:quantum-task_7e1c60a9-c517-4c68-a180-14da89cc1f52"
        self.test_should_retrieve_job(BRAKET_NAME_IONQ_ARIA, BACKEND_ID_AWS_IONQ_ARIA, job_id, 1)

    def test_should_retrieve_job_ionq_harmony(self):
        job_id = "arn:backends:braket:us-east-1:750565748698:quantum-task_0e77afdd-5bcb-455f-8578-48aee3cce30f"
        self.test_should_retrieve_job(BRAKET_NAME_IONQ_HARMONY, BACKEND_ID_AWS_IONQ_HARMONY, job_id, 1)

    def test_should_retrieve_job_rigetti(self):
        job_id = "arn:backends:braket:us-west-1:750565748698:quantum-task_07a67813-2e95-4ba1-803e-427d6610ea79"
        self.test_should_retrieve_job(BRAKET_NAME_RIGETTI_ASPEN, BACKEND_ID_AWS_RIGETTI_ASPEN, job_id, 10)

    def test_should_retrieve_job_oqc_lucy(self):
        job_id = "arn:backends:braket:eu-west-2:750565748698:quantum-task_3da2d55c-7c7a-4654-b7ae-c8552c329245"
        self.test_should_retrieve_job(BRAKET_NAME_OQC_LUCY, BACKEND_ID_AWS_OQC_LUCY, job_id, 10)

    def test_should_retrieve_job_result_sv1(self):
        job_id = "arn:backends:braket:us-east-1:750565748698:quantum-task_f7c4504e-265f-4f2b-943d-3071eadd1824"
        self.test_should_retrieve_job_result(BRAKET_NAME_SV1, BACKEND_ID_AWS_SV1, job_id)

    def test_should_retrieve_job_result_dm1(self):
        job_id = "arn:backends:braket:us-east-1:750565748698:quantum-task_3c37a335-84a8-49a2-b7ca-3e2aafed8d39"
        self.test_should_retrieve_job_result(BRAKET_NAME_DM1, BACKEND_ID_AWS_DM1, job_id)

    def test_should_retrieve_job_result_ionq_aria(self):
        job_id = "arn:backends:braket:us-east-1:750565748698:quantum-task_7e1c60a9-c517-4c68-a180-14da89cc1f52"
        self.test_should_retrieve_job_result(BRAKET_NAME_IONQ_ARIA, BACKEND_ID_AWS_IONQ_ARIA, job_id)

    def test_should_retrieve_job_result_ionq_harmony(self):
        job_id = "arn:backends:braket:us-east-1:750565748698:quantum-task_0e77afdd-5bcb-455f-8578-48aee3cce30f"
        self.test_should_retrieve_job_result(BRAKET_NAME_IONQ_HARMONY, BACKEND_ID_AWS_IONQ_HARMONY, job_id)

    def test_should_retrieve_job_result_rigetti(self):
        job_id = "arn:backends:braket:us-west-1:750565748698:quantum-task_07a67813-2e95-4ba1-803e-427d6610ea79"
        self.test_should_retrieve_job_result(BRAKET_NAME_RIGETTI_ASPEN, BACKEND_ID_AWS_RIGETTI_ASPEN, job_id)

    def test_should_retrieve_job_result_oqc_lucy(self):
        job_id = "arn:backends:braket:eu-west-2:750565748698:quantum-task_3da2d55c-7c7a-4654-b7ae-c8552c329245"
        self.test_should_retrieve_job_result(BRAKET_NAME_OQC_LUCY, BACKEND_ID_AWS_OQC_LUCY, job_id)

    def test_should_cancel_job_ionq_aria(self):
        self.test_should_cancel_job(BACKEND_ID_AWS_IONQ_ARIA, 1)

    def test_should_cancel_job_ionq_harmony(self):
        self.test_should_cancel_job(BACKEND_ID_AWS_IONQ_HARMONY, 1)

    def test_should_cancel_job_rigetti(self):
        self.test_should_cancel_job(BACKEND_ID_AWS_RIGETTI_ASPEN, 10)

    def test_should_cancel_job_oqc_lucy(self):
        self.test_should_cancel_job(BACKEND_ID_AWS_OQC_LUCY, 1)
