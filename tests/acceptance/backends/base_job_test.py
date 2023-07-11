import logging
import os
import unittest
from abc import ABC, abstractmethod
from typing import List

from braket.circuits import Instruction
from busypie import wait
from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit.providers import JobStatus, BackendV2
from qiskit.providers.models import QasmBackendConfiguration
from qiskit.result import Result
from qiskit.result.models import ExperimentResultData, ExperimentResult

from planqk.qiskit.client.client_dtos import JOB_STATUS
from planqk.qiskit.job import PlanqkJob
from planqk.qiskit.provider import PlanqkQuantumProvider
from tests.utils import get_sample_circuit


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
    def is_simulator(self) -> bool:
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
        except Exception as e:
            # Ignore error as this is just cleanup
            logging.warning(f"Could not cancel the job. Error: {str(e)}")

    def _run_job(self) -> PlanqkJob:
        planqk_backend = self.planqk_provider.get_backend(self.get_backend_id())
        self._planqk_job = planqk_backend.run(self.input_circuit, shots=self.get_test_shots())
        return self._planqk_job

    @abstractmethod
    def test_should_get_backend(self):
        pass

    def should_get_backend(self):
        # Get backend via Provider
        expected = self.get_provider().get_backend(self.get_provider_backend_name())

        # Get backend via PlanqkProvider
        actual = self.planqk_provider.get_backend(self.get_backend_id())

        # PlanQK Backend: HARDWARE_PROVIDER.IONQ_CIRCUIT_V1 Aria 1
        self.assertEqual(self.get_backend_id(), actual.name)
        self.assert_num_of_qubits(expected.num_qubits, actual.num_qubits)
        self.assertEqual(expected.backend_version, actual.backend_version)
        self.assertTrue(str(expected.coupling_map), str(actual.coupling_map))
        self.assertTrue(actual.description.startswith("PlanQK Backend:"))
        self.assertTrue(actual.description.endswith(actual.name + "."))
        self.assertEqual(expected.dt, actual.dt)
        # self.assertEqual(backend.instruction_durations, config.instruction_durations)
        self.assertEqual(str(expected.instruction_schedule_map), str(actual.instruction_schedule_map))

        self.assert_instructions(expected.instructions, actual.instructions)
        self.assert_backend_config(expected, actual.configuration())
        self.assertEqual(expected.max_circuits, actual.max_circuits)
        with self.assertRaises(Exception) as backend_exc:
            _ = actual.meas_map()
        with self.assertRaises(Exception) as expected_exc:
            _ = expected.meas_map()
        self.assertEqual(type(backend_exc.exception), type(expected_exc.exception))
        self.assertCountEqual(expected.operation_names, actual.operation_names)
        self.assertCountEqual(str(expected.operations), str(actual.operations))
        self.assertEqual(expected.options, actual.options)
        self.assertEqual(expected.target, actual.target)
        self.assertEqual(expected.version, actual.version)

    def assert_num_of_qubits(self, expected: int, actual: int):
        self.assertEqual(expected, actual)

    def assert_instructions(self, expected: List[Instruction], actual: List[Instruction]):
        # self.assertEqual(len(backend), len(config))
        expected_instruction_strs = [str(entry) for entry in expected]
        actual_instruction_strs = [str(entry) for entry in actual]
        for expected_instruction_str in expected_instruction_strs:
            if expected_instruction_str not in actual_instruction_strs:
                print(f"Expected instruction {expected_instruction_str} not found in actual list")
            # assert expected_instruction_str in actual_instruction_strs, f"Expected instruction {expected_instruction_str} not found in config list"

    def assert_backend_config(self, backend: BackendV2, config: QasmBackendConfiguration):
        self.assertEqual(self.get_backend_id(), config.backend_name)
        self.assertEqual(backend.backend_version, config.backend_version)
        self.assertIsNotNone(config.basis_gates)
        self.assertTrue(len(config.gates) > 0)
        self.assertEqual(False, config.local)
        self.assertEqual(self.is_simulator(), config.simulator)
        self.assertEqual(False, config.conditional)
        self.assertEqual(False, config.open_pulse)
        self.assertIsNotNone(config.memory)
        self.assertTrue(config.max_shots > 0)
        self.assertEqual(backend.coupling_map, config.coupling_map)
        self.assertTrue(config.max_experiments > 0)
        self.assertIsNotNone(config.description)

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

        planqk_job_state = metadata.get('status')
        if planqk_job_state == JOB_STATUS.COMPLETED:
            self.assertIsNotNone(metadata.get('end_execution_time'))
        else:
            self.assertIsNone(metadata.get('end_execution_time'))

        # Check if the other fields have the backend values
        self.assertEqual(metadata.get('backend_id'), planqk_backend_id)
        self.assertEqual(metadata.get('provider'), self.get_provider_id())
        self.assertEqual(metadata.get('shots'), self.get_test_shots())
        self.assertIsNone(metadata.get('input'))
        self.assertIsNone(metadata.get('circuit_type'))
        self.assertIsNone(metadata.get('cancellation_time'))
        self.assertIsNone(metadata.get('error_data'))
        self.assertIsNone(metadata.get('metadata'))
        # This the internal job status name not the Qiskit status name
        self.assertIn(planqk_job_state, [JOB_STATUS.PENDING, JOB_STATUS.RUNNING, JOB_STATUS.COMPLETED])
        self.assertEqual(metadata.get('tags'), [])

    @abstractmethod
    def test_should_retrieve_job_result(self):
        pass

    def should_retrieve_job_result(self):
        # Given:
        planqk_job = self._run_job()
        job_id = planqk_job.id
        planqk_backend_id = self.get_backend_id()

        # Get job via PlanQK
        planqk_backend = self.planqk_provider.get_backend(planqk_backend_id)
        job = planqk_backend.retrieve_job(job_id)
        result: Result = job.result()

        # Get job result via provider
        backend = self.get_provider().get_backend(self.get_provider_backend_name())
        provider_job_id = self.get_provider_job_id(job_id)
        exp_result: Result = backend.retrieve_job(provider_job_id).result()

        self.assertEqual(result.backend_name, planqk_backend_id)
        self.assertEqual(self.get_provider_job_id(result.job_id), exp_result.job_id)
        self.assertEqual(exp_result.success, result.success)
        result_entry: ExperimentResult = result.results[0]
        exp_result_entry: ExperimentResult = exp_result.results[0]
        self.assertEqual(exp_result_entry.shots, result_entry.shots)
        self.assert_experimental_result_data(exp_result_entry.data, result_entry.data)
        self.assertIsNotNone(result.date)

    def assert_experimental_result_data(self, result: ExperimentResultData, exp_result: ExperimentResultData):
        self.assertEqual(exp_result.counts, result.counts)
        self.assertEqual(exp_result.memory, result.memory)

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

    @abstractmethod
    def test_should_retrieve_job_status(self):
        pass

    def should_retrieve_job_status(self):
        # Given:
        planqk_job = self._run_job()

        # When:
        job_status = planqk_job.status()

        # Then:
        self.assertIn(job_status, [JobStatus.QUEUED, JobStatus.DONE, JobStatus.RUNNING])
