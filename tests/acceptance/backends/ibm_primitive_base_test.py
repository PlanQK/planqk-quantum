import os

from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler

from planqk.qiskit import PlanqkJob
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.runtime_provider import PlanqkQiskitRuntimeService
from tests.acceptance.backends.base_test import BaseTest


class IbmPrimitiveBaseTest(BaseTest):
    def setUp(self):
        super().load_env_vars()
        self.assertIsNotNone(os.getenv('IBM_QUANTUM_TOKEN'),
                             "Env variable IBM_QUANTUM_TOKEN (IBM token for quantum channel) not set")
        self.planqk_provider = PlanqkQiskitRuntimeService(access_token=self.planqk_access_token, channel="ibm_quantum")

    def get_provider(self):
        return QiskitRuntimeService(channel="ibm_quantum", token=os.getenv('IBM_QUANTUM_TOKEN'))

    def get_provider_id(self):
        return PROVIDER.IBM.name

    def is_valid_job_id(self, job_id: str) -> bool:
        return len(job_id) > 19

    def _run_job(self) -> PlanqkJob:
        planqk_backend = self.planqk_provider.get_backend(self.get_backend_id())

        #options = Options()
        #options.resilience_level = 1
        #options.optimization_level = 3

        with Session(self.planqk_provider, backend=planqk_backend.name, max_time=None) as session:
            sampler = Sampler(session=session)
            self._planqk_job = sampler.run(self.get_input_circuit, shots=10) #TODO memory=True
            # https://qiskit.org/ecosystem/ibm-runtime/tutorials/how-to-getting-started-with-sampler.html
            session.close()

        return self._planqk_job

    def should_retrieve_job(self):
        planqk_job = self._run_job()
        job_id = planqk_job.id
        planqk_backend_id = self.get_backend_id()

        # Get job via Qiskit runtime
        exp_job = self.get_provider().job(job_id)
        # Get job via PlanQK
        planqk_backend = self.planqk_provider.get_backend(planqk_backend_id)
        job = planqk_backend.retrieve_job(job_id)

        self.assert_job(job, exp_job)

    # Tests

    def test_should_run_multiple_jobs_in_session(self):
        planqk_backend = self.get_provider().get_backend(self.get_backend_id())

        with Session(self.get_provider(), backend=planqk_backend.name, max_time=None) as session:
            sampler = Sampler(session=session)
            job_1 = sampler.run(self.get_input_circuit, shots=10)
            # TODO:
            job_2 = sampler.run(self.get_input_circuit, shots=10)
            session.close()

            # TODO assert job and session ids
