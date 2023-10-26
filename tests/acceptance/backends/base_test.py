import logging
import os
import unittest
from abc import ABC, abstractmethod
from typing import List, Union

import pytest
from busypie import wait
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Instruction
from qiskit.providers import JobStatus, BackendV2, Backend
from qiskit.providers.models import QasmBackendConfiguration
from qiskit.result import Result
from qiskit.result.models import ExperimentResultData, ExperimentResult
from qiskit.transpiler import Target

from planqk.qiskit.client.backend_dtos import STATUS
from planqk.qiskit.client.job_dtos import JOB_STATUS
from planqk.qiskit.job import PlanqkJob
from planqk.qiskit.provider import PlanqkQuantumProvider
from tests.utils import get_sample_circuit


def hasAttr(backend, param):
    pass


class BaseTest(ABC, unittest.TestCase):
    planqk_access_token = None

    def load_env_vars(self):
        load_dotenv()

        self.assertIsNotNone(os.getenv('PLANQK_QUANTUM_BASE_URL'),
                             "Env variable PLANQK_QUANTUM_BASE_URL (PlanQK quantum base url) not set")
        self.assertIsNotNone(os.getenv('PLANQK_ACCESS_TOKEN'),
                             "Env variable PLANQK_ACCESS_TOKEN (PlanQK API access token) not set")

    def setUp(self):
        self.load_env_vars()
        self.planqk_provider = PlanqkQuantumProvider(self.planqk_access_token)

        # Ensure to see the diff of large objects
        self.maxDiff = None

    @property
    def planqk_access_token(self):
        return os.getenv('PLANQK_ACCESS_TOKEN')

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

    def supports_memory_result(self) -> bool:
        return False

    @abstractmethod
    def get_provider_job_id(self, job_id: str) -> str:
        pass

    @abstractmethod
    def is_valid_job_id(self, job_id: str) -> bool:
        pass

    def get_input_circuit(self) -> QuantumCircuit:
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
        if planqk_backend._backend_info.status == STATUS.OFFLINE:
            self.skipTest("Backend {0} is offline. Cannot run job".format(self.get_backend_id()))

        self._planqk_job = planqk_backend.run(self.get_input_circuit(), shots=self.get_test_shots())
        return self._planqk_job

    @abstractmethod
    @pytest.mark.skip(reason='abstract method')
    @pytest.mark.run(order=1)
    def test_should_get_backend(self):
        pass

    def should_get_backend(self):
        # Get actual via Provider
        expected = self.get_provider().get_backend(self.get_provider_backend_name())

        # Get actual via PlanqkProvider
        actual = self.planqk_provider.get_backend(self.get_backend_id())

        self.assertEqual(self.get_backend_id(), actual.name)
        self.assert_backend(expected, actual)

    def assert_backend(self, expected: Union[Backend, BackendV2], actual: BackendV2):
        self.assert_num_of_qubits(expected.num_qubits, actual.num_qubits)
        self.assertIsNotNone(expected.backend_version)
        self.assertTrue(str(expected.coupling_map), str(actual.coupling_map))
        self.assertTrue(actual.description.startswith("PlanQK Backend:"))
        self.assertTrue(actual.description.endswith(actual.name + "."))

        # Just gate based properties are asserted but not pulse based properties

        self.assert_instructions(expected.instructions, actual.instructions)
        self.assert_backend_config(expected, actual.configuration())
        # self.assertEqual(expected.max_circuits, actual.max_circuits) TODO add property
        self.assert_operations(expected.operations, actual.operations)
        # self.assertEqual(expected.options, actual.options) # TODO add default options in backend
        self.assert_target(expected.target, actual.target)

    def assert_instructions(self, exp_instructions: List[Instruction], act_instructions: List[Instruction]):
        # Delete delay instructions as we ignore them
        # exp_instructions = [instruction for instruction in exp_instructions if instruction[0].__class__ != Delay]

        # sort the lists by name and by coupling tuple
        exp_instructions = sorted(sorted(exp_instructions, key=lambda x: x[0].name), key=lambda x: (x[1] is None, x[1]))
        act_instructions = sorted(sorted(act_instructions, key=lambda x: x[0].name), key=lambda x: (x[1] is None, x[1]))

        for i in range(len(exp_instructions)):
            exp_instruction = exp_instructions[i][0]
            actual_instruction = act_instructions[i][0]
            self.assertEqual(exp_instruction.__class__, actual_instruction.__class__,
                             f'Instruction {i} {actual_instruction.name} in iteration has different type')
            self.assertEqual(exp_instruction.condition, actual_instruction.condition,
                             f'Instruction {actual_instruction.name} has different condition')
            self.assertEqual(exp_instruction.condition_bits, actual_instruction.condition_bits,
                             f'Instruction {actual_instruction.name} has different condition bits')
            self.assertEqual(len(exp_instruction.decompositions), len(actual_instruction.decompositions),
                             f'Instruction {actual_instruction.name} has different decompositions')
            self.assertEqual(str(exp_instruction.definition),
                             str(actual_instruction.definition),
                             f'Instruction {actual_instruction.name} has different definition')
            self.assertEqual(str(exp_instruction.duration), str(actual_instruction.duration),
                             f'Instruction {actual_instruction.name} has different duration')
            self.assertEqual(exp_instruction.label, actual_instruction.label,
                             f'Instruction {actual_instruction.name} has different label')
            self.assertEqual(exp_instruction.name, actual_instruction.name,
                             f'Instruction {actual_instruction.name} has different name')
            self.assertEqual(exp_instruction.num_clbits, actual_instruction.num_clbits,
                             f'Instruction {actual_instruction.name} has different number of clbits')
            self.assertEqual(exp_instruction.num_qubits, actual_instruction.num_qubits,
                             f'Instruction {actual_instruction.name} has different number of qubits')
            self.assertEqual(str(exp_instruction.params), str(actual_instruction.params),
                             f'Instruction {actual_instruction.name} has different params')
            self.assertEqual(exp_instruction.unit, actual_instruction.unit,
                             f'Instruction {actual_instruction.name} has different unit')
            self.assertEqual(exp_instructions[i][1], act_instructions[i][1],
                             f'Instruction {actual_instruction.name} has different coupling tuple')

        self.assertEqual(len(exp_instructions), len(act_instructions), 'Different number of instructions')

    def assert_num_of_qubits(self, expected: int, actual: int):
        self.assertEqual(expected, actual)

    def assert_backend_config(self, backend: Union[Backend, BackendV2], config: QasmBackendConfiguration):
        self.assertEqual(self.get_backend_id(), config.backend_name)
        self.assertEqual('2', config.backend_version)
        self.assertIsNotNone(config.basis_gates)
        self.assertTrue(len(config.gates) >= 0)
        self.assertEqual(False, config.local)
        self.assertEqual(self.is_simulator(), config.simulator)
        self.assertEqual(False, config.conditional)
        self.assertEqual(False, config.open_pulse)
        self.assertEqual(self.supports_memory_result(), config.memory)
        self.assertTrue(config.max_shots > 0)
        if hasattr(backend, 'coupling_map') and backend.coupling_map is not None:
            self.assertEqual(backend.coupling_map, config.coupling_map)
        self.assertTrue(config.max_experiments > 0)
        self.assertIsNotNone(config.description)

    def assert_operation_names(self, expected: List[str], actual: List[str]):
        exp_operation_names = [op_name for op_name in expected.operation_names if
                               op_name != 'delay']  # TODO override in IBM
        self.assertEqual(sorted(exp_operation_names), sorted(actual.operation_names))

    def assert_operations(self, expected: List[Instruction], actual: List[Instruction]):
        # Operation properties are not asserted since this was already done in assert_instructions
        self.assertEqual(len(expected), len(actual))

    def assert_target(self, expected: Target, actual: Target):
        # Instruction properties are not asserted since this was already done in assert_instructions
        self.assertEqual(expected.num_qubits, actual.num_qubits)
        self.assertEqual(expected.physical_qubits, actual.physical_qubits)
        self.assertEqual(expected.qargs, actual.qargs)

    @abstractmethod
    @pytest.mark.skip(reason='abstract method')
    def test_should_transpile_circuit(self):
        pass

    def should_transpile_circuit(self):
        # Transpile via Provider
        backend = self.get_provider().get_backend(self.get_provider_backend_name())
        expected = transpile(self.get_input_circuit(), backend=backend)

        # Transpile via PlanQK
        planqk_backend = self.planqk_provider.get_backend(self.get_backend_id())
        actual = transpile(self.get_input_circuit(), backend=planqk_backend)

        self.assert_transpile_result(expected, actual)

    def assert_transpile_result(self, expected, actual):
        self.assertEqual(expected.header, actual.header)
        self.assertEqual(str(expected), str(actual))

    @abstractmethod
    @pytest.mark.skip(reason='abstract method')
    def test_should_run_job(self):
        pass

    def should_run_job(self):
        self._planqk_job = self._run_job()
        self.is_valid_job_id(self._planqk_job.id)

    @abstractmethod
    @pytest.mark.skip(reason='abstract method')
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

        self.assert_job(job, exp_job)

    def assert_job(self, job, exp_job):
        # Braket Qiskit job objects no metadata, hence, we cannot compare the objects except for the job id
        self.assertEqual(self.get_provider_job_id(job.job_id()), exp_job.job_id())

        metadata = job.metadata
        self.assertIsNotNone(metadata.get('id'))
        self.assertIsNotNone(metadata.get('name'))
        self.assertIsNotNone(metadata.get('creation_time'))

        planqk_job_state = metadata.get('status')

        # Check if the other fields have the actual values
        self.assertEqual(metadata.get('backend_id'), self.get_backend_id())
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
    @pytest.mark.skip(reason='abstract method')
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

        self.assert_result(exp_result, result)

    def assert_result(self, exp_result: Result, result: Result):
        self.assertEqual(exp_result.success, result.success)
        result_entry: ExperimentResult = result.results[0]
        exp_result_entry: ExperimentResult = exp_result.results[0]
        self.assertEqual(exp_result_entry.shots, result_entry.shots)
        self.assert_experimental_result_data(exp_result_entry.data, result_entry.data)
        self.assertIsNotNone(result.date)

    def assert_experimental_result_data(self, exp_result: ExperimentResultData, result: ExperimentResultData):
        self.assertEqual(exp_result.counts, result.counts)
        self.assertEqual(exp_result.memory, result.memory)

    @abstractmethod
    @pytest.mark.skip(reason='abstract method')
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
    @pytest.mark.skip(reason='abstract method')
    def test_should_retrieve_job_status(self):
        pass

    def should_retrieve_job_status(self):
        # Given:
        planqk_job = self._run_job()

        # When:
        job_status = planqk_job.status()

        # Then:
        self.assertIn(job_status, [JobStatus.QUEUED, JobStatus.DONE, JobStatus.RUNNING])
