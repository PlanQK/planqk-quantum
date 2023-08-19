import os
from typing import List

from qiskit import QuantumCircuit
from qiskit.circuit import Measure, Instruction
from qiskit_ibm_runtime import Session, Sampler, Options, QiskitRuntimeService

from planqk.qiskit import PlanqkJob
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.runtime_provider import PlanqkQiskitRuntimeService
from tests.acceptance.backends.backends_list import BACKEND_ID_IBM_LAGOS, BACKEND_ID_IBM_QASM_SIM
from tests.acceptance.backends.base_test import BaseTest
from tests.acceptance.backends.ibm_test_utils import IBM_QASM_SIMULATOR_NAME
from tests.utils import get_width_sample_circuit


class IbmPrimitiveQasmSimulatorTests(BaseTest):

    def setUp(self):
        super().load_env_vars()
        self.assertIsNotNone(os.getenv('IBM_QUANTUM_TOKEN'),
                             "Env variable IBM_QUANTUM_TOKEN (IBM token for quantum channel) not set")
        self.planqk_provider = PlanqkQiskitRuntimeService(access_token=self.planqk_access_token, channel="ibm_quantum")

    def get_provider(self):
        return QiskitRuntimeService(channel="ibm_quantum", token=os.getenv('IBM_QUANTUM_TOKEN'))

    def get_provider_id(self):
        return PROVIDER.IBM.name

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

    def get_provider_job_id(self, job_id: str) -> str:
        return job_id

    def is_valid_job_id(self, job_id: str) -> bool:
        return len(job_id) > 19

    def _run_job(self) -> PlanqkJob:
        planqk_backend = self.planqk_provider.get_backend(self.get_backend_id())

        #options = Options()
        #options.resilience_level = 1
        #options.optimization_level = 3

        with Session(self.planqk_provider, backend=planqk_backend.name, max_time=None) as session:
            sampler = Sampler(session=session)
            self._planqk_job = sampler.run(self.get_input_circuit(), shots=1000) #TODO memory=True
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


    def assert_instructions(self, exp_instructions: List[Instruction], act_instructions: List[Instruction]):
        # Qiskit creates a one measure instruction forall qubits we provide a measure instruction for each qubit
        act_instructions = [instruction for instruction in act_instructions if instruction[0].name != "measure"]
        act_instructions.append(tuple([Measure(), None]))
        super().assert_instructions(exp_instructions, act_instructions)

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
        planqk_backend = self.get_provider().get_backend(self.get_backend_id())

        with Session(self.get_provider(), backend=planqk_backend.name, max_time=None) as session:
            sampler = Sampler(session=session)
            job_1 = sampler.run(self.get_input_circuit, shots=10)
            #TODO:
            job_2 = sampler.run(self.get_input_circuit, shots=10)
            session.close()

    def test_should_retrieve_job(self):
        self.should_retrieve_job()

    def test_should_retrieve_job_result(self):
        self.should_retrieve_job_result()

    def test_should_cancel_job(self):
        self.should_cancel_job()

    def test_should_retrieve_job_status(self):
        self.should_retrieve_job_status()
