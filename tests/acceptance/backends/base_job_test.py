import logging
import os
import unittest
from abc import ABC, abstractmethod

from busypie import wait
from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit.providers import JobStatus
from qiskit.result import Result
from qiskit.result.models import ExperimentResultData, ExperimentResult

from planqk.exceptions import PlanqkClientError
from planqk.qiskit.client.client_dtos import JOB_STATUS
from planqk.qiskit.job import PlanqkJob
from planqk.qiskit.provider import PlanqkQuantumProvider
from tests.utils import to_dict, get_sample_circuit


class BaseJobTest(ABC, unittest.TestCase):
    def setUp(self):
        load_dotenv()

        PLANQK_QUANTUM_BASE_URL = os.getenv('PLANQK_QUANTUM_BASE_URL')
        PLANQK_ACCESS_TOKEN = os.getenv('PLANQK_ACCESS_TOKEN')

        self.assertIsNotNone(PLANQK_QUANTUM_BASE_URL,
                             "Env variable PLANQK_QUANTUM_BASE_URL (PlanQK quantum base url) not set")
        self.assertIsNotNone(PLANQK_ACCESS_TOKEN,
                             "Env variable PLANQK_ACCESS_TOKEN (PlanQK API access token) not set")

        self.planqk_provider = PlanqkQuantumProvider(PLANQK_ACCESS_TOKEN)

        # Ensure to see the diff of large objects
        self.maxDiff = None

    @abstractmethod
    def get_provider(self):
        pass

    @abstractmethod
    def get_provider_id(self):
        pass

    @abstractmethod
    def get_backend_id(self) -> str:
        pass

    @abstractmethod
    def get_provider_backend_name(self) -> str:
        pass

    @abstractmethod
    def get_test_shots(self):
        pass

    @abstractmethod
    def is_simulator(self, backend_id: str) -> bool:
        pass

    @abstractmethod
    def get_provider_job_id(self, job_id: str) -> str:
        pass

    @abstractmethod
    def is_valid_job_id(self, job_id: str) -> bool:
        pass

    @property
    def input_circuit(self) -> QuantumCircuit:
        return get_sample_circuit()

    def get_provider_job_id(self, job_id: str) -> str:
        return job_id

    def tearDown(self):
        # Cancel job to avoid costs
        try:
            if hasattr(self, '_planqk_job') and self._planqk_job is not None:
                self._planqk_job.cancel()
        except PlanqkClientError as e:
            # Ignore error as this is just cleanup
            logging.warning(f"Could not cancel the job. Error: {str(e)}")

    def _run_job(self) -> PlanqkJob:
        planqk_backend = self.planqk_provider.get_backend(self.get_backend_id())
        self._planqk_job = planqk_backend.run(self.input_circuit, shots=self.get_test_shots())
        return self._planqk_job

    @abstractmethod
    def test_should_run_job(self):
        pass

    def should_run_job(self):
        self._planqk_job = self._run_job()
        self.is_valid_job_id(self._planqk_job.id)

    @abstractmethod
    def test_should_retrieve_job(self):
        pass

    def should_retrieve_job(self):
        planqk_job = self._run_job()
        job_id = planqk_job.id
        planqk_backend_id = self.get_backend_id()

        # Get job via Provider
        backend = self.get_provider().get_backend(self.get_provider_backend_name())
        exp_job = backend.retrieve_job(self.get_provider_job_id(job_id))

        # Get job via PlanQK
        planqk_backend = self.planqk_provider.get_backend(planqk_backend_id)
        job = planqk_backend.retrieve_job(job_id)

        # Braket Qiskit job objects no metadata, hence, we cannot compare the objects except for the job id
        self.assertEqual(self.get_provider_job_id(job.job_id()), exp_job.job_id())

        metadata = job.metadata
        self.assertIsNotNone(metadata.get('id'))
        self.assertIsNotNone(metadata.get('name'))
        self.assertIsNotNone(metadata.get('creation_time'))
        self.assertIsNotNone(metadata.get('end_execution_time'))

        # Check if the other fields have the expected values
        self.assertEqual(metadata.get('backend_id'), planqk_backend_id)
        self.assertEqual(metadata.get('provider'), self.get_provider_id())
        self.assertEqual(metadata.get('shots'), self.get_test_shots())
        self.assertIsNone(metadata.get('input'))
        self.assertIsNone(metadata.get('circuit_type'))
        self.assertEqual(metadata.get('input_params').get('qubit_count'), 3)
        self.assertIsNone(metadata.get('begin_execution_time'))
        self.assertIsNone(metadata.get('cancellation_time'))
        self.assertIsNone(metadata.get('error_data'))
        self.assertIsNone(metadata.get('metadata'))
        # This the internal job status name not the Qiskit status name
        self.assertIn(metadata.get('status'), [JOB_STATUS.PENDING, JOB_STATUS.RUNNING, JOB_STATUS.COMPLETED])
        self.assertEqual(metadata.get('tags'), [])

    @abstractmethod
    def test_should_retrieve_job_result(self):
        pass

    def should_retrieve_job_result(self):
        # Given:
        planqk_job = self._run_job()
        planqk_backend_id = self.get_backend_id()

        # Get job result via provider
        backend = self.get_provider().get_backend(self.get_provider_backend_name())
        provider_job_id = self.get_provider_job_id(planqk_job.id)
        exp_result: Result = backend.retrieve_job(provider_job_id).result()

        # Get job via PlanQK
        planqk_backend = self.planqk_provider.get_backend(planqk_backend_id)
        job = planqk_backend.retrieve_job(planqk_job.id)
        job_result_dict = to_dict(job.result())
        result: Result = job.result()

        self.assertEqual(result.backend_name, planqk_backend_id)
        self.assertEqual(self.get_provider_job_id(result.job_id), exp_result.job_id)
        self.assertEqual(result.success, exp_result.success)
        result_entry: ExperimentResult = result.results[0]
        exp_result_entry: ExperimentResult = exp_result.results[0]
        self.assertEqual(result_entry.shots, exp_result_entry.shots)
        self.assert_experimental_result_data(result_entry.data, exp_result_entry.data,
                                             self.is_simulator(planqk_backend_id))
        self.assertIsNotNone(job_result_dict['date'])

    def assert_experimental_result_data(self, result: ExperimentResultData, exp_result: ExperimentResultData,
                                        is_random_result=False):
        self.assertEqual(result.counts, exp_result.counts)
        self.assertEqual(result.memory, exp_result.memory)

    @abstractmethod
    def test_should_cancel_job(self):
        pass

    def should_cancel_job(self):
        # Given:
        planqk_job = self._run_job()

        # When:
        planqk_job.cancel()

        def assert_job_cancelled():
            job_status = planqk_job.status()
            assert job_status == JobStatus.CANCELLED

        # Then:
        wait().until_asserted(assert_job_cancelled)
