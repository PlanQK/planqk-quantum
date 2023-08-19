import os
from typing import List

from qiskit.circuit import Instruction, Delay, Measure
from qiskit_ibm_runtime import Session, Sampler, Options, QiskitRuntimeService

from planqk.qiskit import PlanqkJob
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.runtime_provider import PlanqkQiskitRuntimeService
from tests.acceptance.backends.backends_list import BACKEND_ID_IBM_LAGOS, BACKEND_ID_IBM_QASM_SIM, \
    BACKEND_ID_IBM_NAIROBI
from tests.acceptance.backends.base_test import BaseTest
from tests.acceptance.backends.ibm_primitive_base_test import IbmPrimitiveBaseTest
from tests.acceptance.backends.ibm_test_utils import IBM_QASM_SIMULATOR_NAME, IBM_NAIROBI_NAME


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

    def get_provider_job_id(self, job_id: str) -> str:
        return job_id

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
