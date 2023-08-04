from qiskit_ibm_runtime import Session, Sampler, Options

from planqk.qiskit import PlanqkJob
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.runtime_provider import PlanqkQiskitRuntimeService
from tests.acceptance.backends.backends_list import BACKEND_ID_IBM_LAGOS, BACKEND_ID_IBM_QASM_SIM
from tests.acceptance.backends.base_test import BaseTest

API_TOKEN = "2d9b5e56d8cb73ae8d8499bc541552aa54647a8d9be85b475530ea75044f2226eb2e42d26821e5fa21328989496f6da914fae0bf3054ac730ce6bc79dd73b0ff"


class IbmPrimitiveLagosTests(BaseTest):

    def setUp(self):
        super().load_env_vars()
        self.qiskit_runtime = PlanqkQiskitRuntimeService(access_token=self.planqk_access_token, channel="ibm_quantum")

    def get_provider(self):
        return self.qiskit_runtime

    def get_provider_id(self):
        return PROVIDER.IBM.name

    def get_backend_id(self) -> str:
        return BACKEND_ID_IBM_QASM_SIM

    def get_provider_backend_name(self) -> str:
        return "ibmq_qasm_simulator"

    def get_test_shots(self) -> int:
        return 10

    def is_simulator(self) -> bool:
        return False

    def get_provider_job_id(self, job_id: str) -> str:
        return job_id

    def is_valid_job_id(self, job_id: str) -> bool:
        return len(job_id) > 19

    def _run_job(self) -> PlanqkJob:
        # TODO just return backend ids
        # TODO how to handle missing backend token? should do this in SDK if backend is empty
        planqk_backend = self.get_provider().get_backend(self.get_backend_id())

        options = Options()
        options.resilience_level = 1
        options.optimization_level = 3

        with Session(self.get_provider(), backend=planqk_backend.name, max_time=None) as session:
            sampler = Sampler(session=session, options=options)
            self._planqk_job = sampler.run(self.input_circuit, shots=10) #TODO memory=True
            # https://qiskit.org/ecosystem/ibm-runtime/tutorials/how-to-getting-started-with-sampler.html
            self._planqk_job.result()
            #TODO result returned nicht read eror mitigation
            session.close()

        return self._planqk_job

    # Tests

    def test_should_get_backend(self):
        self.should_get_backend()

    def test_should_transpile_circuit(self):
        self.should_transpile_circuit()

    def test_should_run_job(self):
        self.should_run_job()

    def test_should_run_multiple_jobs_in_session(self):
        planqk_backend = self.get_provider().get_backend(self.get_backend_id())

        with Session(self.get_provider(), backend=planqk_backend.name, max_time=None) as session:
            sampler = Sampler(session=session)
            job_1 = sampler.run(self.input_circuit, shots=10)
            #TODO:
            job_2 = sampler.run(self.input_circuit, shots=10)
            session.close()

    def test_should_retrieve_job(self):
        self.should_retrieve_job()

    def test_should_retrieve_job_result(self):
        self.should_retrieve_job_result()

    def test_should_cancel_job(self):
        self.should_cancel_job()

    def test_should_retrieve_job_status(self):
        self.should_retrieve_job_status()
