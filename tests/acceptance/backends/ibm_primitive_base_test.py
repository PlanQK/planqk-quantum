import logging
import os
from abc import abstractmethod

import pytest
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Estimator

from planqk.qiskit import PlanqkJob, PlanqkQuantumProvider
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.runtime_provider import PlanqkQiskitRuntimeService
from tests.acceptance.backends.base_test import BaseTest
from tests.utils import get_estimator_circuit


class IbmPrimitiveBaseTest(BaseTest):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._planqk_runtime_jobs = []

    def setUp(self):
        super().load_env_vars()
        self.assertIsNotNone(os.getenv('IBM_QUANTUM_TOKEN'),
                             "Env variable IBM_QUANTUM_TOKEN (IBM token for quantum channel) not set")
        self.planqk_provider = PlanqkQiskitRuntimeService(access_token=self.planqk_access_token, channel="ibm_quantum")

    def tearDown(self):
        # Cancel job to avoid costs
        super().tearDown()
        if hasattr(self, '_planqk_runtime_jobs') and self._planqk_runtime_jobs is not None:
            for job in self._planqk_runtime_jobs:
                try:
                    job.cancel()
                except Exception as e:
                    # Ignore error as this is just cleanup
                    logging.warning(f"Could not cancel the job. Error: {str(e)}")
        self._planqk_runtime_jobs = []

    def get_provider(self):
        return QiskitRuntimeService(channel="ibm_quantum", token=os.getenv('IBM_QUANTUM_TOKEN'))

    def get_provider_id(self):
        return PROVIDER.IBM.name

    def is_valid_job_id(self, job_id: str) -> bool:
        return len(job_id) > 19

    def get_provider_job_id(self, job_id: str) -> str:
        return job_id

    def _run_job(self) -> PlanqkJob:
        planqk_backend = self.planqk_provider.get_backend(self.get_backend_id())

        # options = Options()
        # options.resilience_level = 1
        # options.optimization_level = 3

        with Session(self.planqk_provider, backend=planqk_backend.name, max_time=None) as session:
            sampler = Sampler(session=session)
            self._planqk_job = sampler.run(self.get_input_circuit(), shots=10)  # TODO memory=True
            session.close()
        return self._planqk_job

    def should_not_run_job_with_classic_provider(self):
        classic_provider = PlanqkQuantumProvider(self.planqk_access_token)
        planqk_backend = classic_provider.get_backend(self.get_backend_id())
        with self.assertRaises(ValueError):
            planqk_backend.run(self.get_input_circuit(), shots=self.get_test_shots())

    @abstractmethod
    @pytest.mark.skip(reason='abstract method')
    def test_should_run_multiple_jobs_in_session(self):
        pass

    def should_run_multiple_jobs_in_session(self):
        planqk_backend = self.planqk_provider.get_backend(self.get_backend_id())

        with Session(self.planqk_provider, backend=planqk_backend.name, max_time=None) as session:
            sampler = Sampler(session=session)
            job_1 = sampler.run(self.get_input_circuit(), shots=10)
            self._planqk_runtime_jobs.append(job_1)
            job_2 = sampler.run(self.get_input_circuit(), shots=10)
            self._planqk_runtime_jobs.append(job_2)

            self.assertEqual(job_1.session_id, job_2.session_id)
            session.close()

    def should_retrieve_job(self):
        planqk_rt_job = self._run_job()
        job_id = planqk_rt_job.id
        planqk_backend_id = self.get_backend_id()

        # Get job via Qiskit runtime
        exp_job = self.get_provider().job(job_id)
        # Get job via PlanQK
        job = self.planqk_provider.job(job_id)

        self.assert_job(job, exp_job)

    def should_retrieve_job_result(self):
        # Given:
        planqk_rt_job = self._run_job()
        job_id = planqk_rt_job.id

        # Get result via PlanQK
        result: SamplerResult = planqk_rt_job.result()

        # Get job result via Qiskit runtime
        exp_job = self.get_provider().job(job_id)
        exp_result: SamplerResult = exp_job.result()

        self.assert_sampler_result(exp_result, result)

    @abstractmethod
    @pytest.mark.skip(reason='abstract method')
    def test_should_retrieve_estimator_job_result(self):
        pass

    def should_retrieve_estimator_job_result(self):
        planqk_backend = self.planqk_provider.get_backend(self.get_backend_id())

        # Given: Estimator job
        with Session(self.planqk_provider, backend=planqk_backend.name, max_time=None) as session:
            estimator_params = get_estimator_circuit()
            estimator = Estimator(session=session)
            self._planqk_job = estimator.run(**estimator_params)
            session.close()

        # Get result via PlanQK
        result: EstimatorResult = self._planqk_job.result()

        # Get job result via Qiskit runtime
        exp_job = self.get_provider().job(self._planqk_job.job_id())
        exp_result: EstimatorResult = exp_job.result()

        self.assert_estimator_result(exp_result, result)

    def assert_sampler_result(self, exp_result: SamplerResult, result: SamplerResult):
        # Assertions for quasi_dists
        self.assertEqual(len(result.quasi_dists), len(exp_result.quasi_dists))
        for exp_quasi_dist, res_quasi_dist in zip(exp_result.quasi_dists, result.quasi_dists):
            self.assertEqual(res_quasi_dist, exp_quasi_dist)

        # Assertions for metadata
        self.assertEqual(len(result.metadata), len(exp_result.metadata))
        for exp_meta, res_meta in zip(exp_result.metadata, result.metadata):
            self.assertEqual(res_meta, exp_meta)

    def assert_estimator_result(self, exp_result: EstimatorResult, result: EstimatorResult):
        # Assertions for values
        self.assertTrue((exp_result.values == result.values).all())

        # Assertions for metadata
        self.assertEqual(len(result.metadata), len(exp_result.metadata))
        for exp_meta, res_meta in zip(exp_result.metadata, result.metadata):
            self.assertEqual(res_meta, exp_meta)
