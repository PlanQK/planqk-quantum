import os

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService

from tests.acceptance.backends.backends_list import BACKEND_ID_IBM_CLOUD_BRISBANE, BACKEND_ID_IBM_CLOUD_CUSCO, \
    BACKEND_ID_IBM_CLOUD_KYIV, BACKEND_ID_IBM_CLOUD_NAZCA, BACKEND_ID_IBM_CLOUD_SHERBROOKE
from tests.acceptance.backends.ibm_primitive_base_test import IbmPrimitiveBaseTest
from tests.acceptance.backends.ibm_test_utils import IBM_BRISBANE_NAME, IBM_CUSCO_NAME, IBM_KYIV_NAME, IBM_NAZCA, \
    IBM_SHERBROOKE
from tests.utils import get_width_sample_circuit


class IbmPrimitiveEagleBackendsTests(IbmPrimitiveBaseTest):

    def __init__(self, name):
        super().__init__(name)
        self._ibm_eagle_backends = {BACKEND_ID_IBM_CLOUD_BRISBANE: IBM_BRISBANE_NAME,
                                    BACKEND_ID_IBM_CLOUD_CUSCO: IBM_CUSCO_NAME,
                                    BACKEND_ID_IBM_CLOUD_KYIV: IBM_KYIV_NAME,
                                    BACKEND_ID_IBM_CLOUD_NAZCA: IBM_NAZCA,
                                    BACKEND_ID_IBM_CLOUD_SHERBROOKE: IBM_SHERBROOKE}
        self._backend_id = None
        self._provider_backend_name = None

    def setUp(self):
        super().setUp()
        self.assertIsNotNone(os.getenv('IBM_CLOUD_API_TOKEN'), "Env variable IBM_CLOUD_API_TOKEN is not set")
        self.assertIsNotNone(os.getenv('IBM_CLOUD_CRN'), "Env variable IBM_CLOUD_CRN is not set")

        # IBM rotates the available Eagle backends, so we need to check which one is available
        available_backends = [(backend_id, self._ibm_eagle_backends[backend_id]) for backend_id in
                              self.planqk_provider.backends() if backend_id in self._ibm_eagle_backends]
        if len(available_backends) == 0:
            self.skipTest("No IBM Eagle backend available")

        self._backend_id, self._provider_backend_name = available_backends[0]

    def get_provider(self):
        return QiskitRuntimeService(channel='ibm_cloud', instance=os.getenv('IBM_CLOUD_CRN'),
                                    token=os.getenv('IBM_CLOUD_API_TOKEN'))

    def get_backend_id(self) -> str:
        return self._backend_id

    def get_provider_backend_name(self) -> str:
        return self._provider_backend_name

    def get_test_shots(self) -> int:
        return 10

    def is_simulator(self) -> bool:
        return False

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
        # self.should_run_job()
        pass

    def test_should_run_multiple_jobs_in_session(self):
        # self.should_run_multiple_jobs_in_session()
        pass

    def test_should_retrieve_job(self):
        # self.should_retrieve_job()
        pass

    def test_should_retrieve_job_result(self):
        # self.should_retrieve_job_result()
        pass

    def test_should_retrieve_estimator_job_result(self):
        # self.should_retrieve_estimator_job_result()
        pass

    def test_should_cancel_job(self):
        # Canceling jobs is not possible as simulator jobs complete instantly
        pass

    def test_should_retrieve_job_status(self):
        pass
