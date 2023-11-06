import pytest
from qiskit import QuantumCircuit

from tests.acceptance.backends.backends_list import BACKEND_ID_IBM_QASM_SIM
from tests.acceptance.backends.ibm_primitive_base_test import IbmPrimitiveBaseTest
from tests.acceptance.backends.ibm_test_utils import IBM_QASM_SIMULATOR_NAME
from tests.utils import get_width_sample_circuit


@pytest.mark.ibm_quantum
class IbmPrimitiveQasmSimulatorTests(IbmPrimitiveBaseTest):

    def get_backend_id(self) -> str:
        return BACKEND_ID_IBM_QASM_SIM

    def get_provider_backend_name(self) -> str:
        return IBM_QASM_SIMULATOR_NAME

    def get_test_shots(self) -> int:
        return 10

    def is_simulator(self) -> bool:
        return True

    def supports_memory_result(self) -> bool:
        return True

    def get_input_circuit(self) -> QuantumCircuit:
        return get_width_sample_circuit(1)

    # Tests

    def test_should_get_backend(self):
        self.should_get_backend()

    def test_should_transpile_circuit(self):
        self.should_transpile_circuit()

    def test_should_run_job(self):
        self.should_run_job()

    def test_should_run_multiple_jobs_in_session(self):
        self.should_run_multiple_jobs_in_session()

    def test_should_retrieve_job(self):
        self.should_retrieve_job()

    def test_should_retrieve_job_result(self):
        self.should_retrieve_job_result()

    def test_should_retrieve_estimator_job_result(self):
        self.should_retrieve_estimator_job_result()

    def test_should_cancel_job(self):
        # Canceling jobs is not possible as simulator jobs complete instantly
        pass

    def test_should_retrieve_job_status(self):
        self.should_retrieve_job_status()
