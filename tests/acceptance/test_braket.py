import logging
import os
import re
import sys
import unittest
from io import StringIO
from typing import List

from busypie import wait
from dotenv import load_dotenv
from qiskit.circuit import Instruction
from qiskit.providers import JobStatus, Backend
from qiskit.tools import job_monitor
from qiskit_braket_provider.providers import AWSBraketProvider

from planqk.qiskit.provider import PlanqkQuantumProvider
from tests.utils import get_sample_circuit

logging.basicConfig(level=logging.DEBUG)

PLANQK_QUANTUM_BASE_URL = os.environ.get('PLANQK_QUANTUM_BASE_URL')
PLANQK_ACCESS_TOKEN = os.environ.get('PLANQK_ACCESS_TOKEN')

SUPPORTED_BACKENDS = {'Aria 1', 'Harmony 2', 'Lucy', 'Aspen-M-3', 'SV1'}


def is_valid_aws_arn(arn_string):
    """
    Validate if the given string is a valid AWS ARN.

    :param arn_string: The ARN string to be validated.
    :return: True if the ARN string is valid, otherwise False.
    """
    arn_pattern = re.compile(
        r'^arn:(aws[a-zA-Z0-9-]*):([a-zA-Z0-9-]+):([a-zA-Z0-9-]*):(\d{12}):([a-zA-Z0-9-/:\._]+)$'
    )
    return bool(arn_pattern.match(arn_string))


def job_id_to_aws_arn(job_id: str) -> str:
    """
    Convert a job id to an AWS ARN.

    :param job_id: The job id to be converted.
    :return: The converted AWS ARN.
    """
    return job_id.replace('_', '/')


class AwsBraketTestSuite(unittest.TestCase):

    def setUp(self):
        # TODO remind to set env variables for AWS

        load_dotenv()

        PLANQK_QUANTUM_BASE_URL = os.getenv('PLANQK_QUANTUM_BASE_URL')
        PLANQK_ACCESS_TOKEN = os.getenv('PLANQK_ACCESS_TOKEN')

        self.assertIsNotNone(PLANQK_QUANTUM_BASE_URL,
                             "Env variable PLANQK_QUANTUM_BASE_URL (PlanQK quantum base url) not set")
        self.assertIsNotNone(PLANQK_ACCESS_TOKEN,
                             "Env variable PLANQK_ACCESS_TOKEN (PlanQK API access token) not set")

        self.braket_provider = AWSBraketProvider()
        self.planqk_provider = PlanqkQuantumProvider(PLANQK_ACCESS_TOKEN)

        # Ensure to see the diff of large objects
        self.maxDiff = None

    def test_should_list_all_backends(self):
        # Get backend names via AWS Braket
        exp_backend_names = []
        exp_backends = self.braket_provider.backends()
        for backend in exp_backends:
            exp_backend_names.append(backend.name)

        # Get backend names via PlanqkProvider
        backend_names = []
        backends = self.planqk_provider.backends()
        for backend in backends:
            backend_names.append(backend.name)

        assert set(backend_names) == set(exp_backend_names).intersection(SUPPORTED_BACKENDS)

        exp_backends_dict = {backend.name: backend for backend in exp_backends}
        # Assert backend properties
        for backend in backends:
            exp_backend = exp_backends_dict[backend.name]
            self.assertBackend(exp_backend, backend)

    def assertBackend(self, expected: Backend, actual: Backend):
        # PlanQK Backend: HARDWARE_PROVIDER.IONQ Aria 1
        self.assertEqual(expected.name, actual.name)
        self.assertEqual(expected.num_qubits, actual.num_qubits)
        self.assertEqual(expected.backend_version, actual.backend_version)
        self.assertTrue(str(expected.coupling_map), str(actual.coupling_map))
        self.assertTrue(actual.description.startswith("PlanQK Backend:"))
        self.assertTrue(actual.description.endswith(actual.name + "."))
        self.assertEqual(expected.dt, actual.dt)
        # self.assertEqual(expected.instruction_durations, actual.instruction_durations)
        self.assertEqual(str(expected.instruction_schedule_map), str(actual.instruction_schedule_map))
        #self.assertEqual(str(expected.instructions), str(actual.instructions))
        self.assert_instructions(expected.instructions, actual.instructions)
        self.assertEqual(expected.max_circuits, actual.max_circuits)
        with self.assertRaises(Exception) as backend_exc:
            _ = actual.meas_map()
        with self.assertRaises(Exception) as expected_exc:
            _ = expected.meas_map()
        self.assertEqual(type(backend_exc.exception), type(expected_exc.exception))
        # self.assertEqual(expected.online_date.replace(microsecond=0).astimezone(None), actual.online_date.astimezone(None))
        self.assertCountEqual(expected.operation_names, actual.operation_names)
        self.assertCountEqual(str(expected.operations), str(actual.operations))
        self.assertEqual(expected.options, actual.options)
        self.assertEqual('_PlanqkAWSBraketProvider', type(actual.provider).__name__)
        self.assertEqual(expected.target, actual.target)
        self.assertEqual(expected.version, actual.version)


    def assert_instructions(self, expected: List[Instruction], actual: List[Instruction]):
        #self.assertEqual(len(expected), len(actual))
        expected_instruction_strs = [str(entry) for entry in expected]
        actual_instruction_strs = [str(entry) for entry in actual]
        for expected_instruction_str in expected_instruction_strs:
            if expected_instruction_str not in actual_instruction_strs:
                print(f"Expected instruction {expected_instruction_str} not found in actual list")
            #assert expected_instruction_str in actual_instruction_strs, f"Expected instruction {expected_instruction_str} not found in actual list"

    def test_should_get_backend(self):
        exp_backend = self.braket_provider.get_backend("Lucy")

        # Get backend via PlanqkProvider
        backend = self.planqk_provider.get_backend("Lucy")
        self.assertBackend(exp_backend, backend)

    def test_should_run_job(self):
        sim_backend = self.planqk_provider.get_backend("SV1")
        # TODO why are getBackends called so often
        circuit = get_sample_circuit(sim_backend)
        job = sim_backend.run(circuit)
        is_valid_aws_arn(job.job_id())

    def test_should_retrieve_job(self):
        # Given: create job
        planqk_backend = self.planqk_provider.get_backend("SV1")

        circuit = get_sample_circuit(planqk_backend)
        created_job = planqk_backend.run(circuit, shots=1)

        # When

        # Get job via AWS
        aws_backend = self.braket_provider.get_backend("SV1")
        exp_job = aws_backend.retrieve_job(created_job.job_id())

        # Get job via PlanQK
        job = planqk_backend.retrieve_job(created_job.job_id())

        # Braket Qiskit job objects no metadata, hence, we cannot compare the objects except for the job id
        assert exp_job.job_id() == job.job_id()

        metadata = job.metadata
        self.assertIsNotNone(metadata.get('id'))
        self.assertIsNotNone(metadata.get('name'))
        self.assertIsNotNone(metadata.get('creation_time'))
        self.assertIsNotNone(metadata.get('end_execution_time'))

        # Check if the other fields have the expected values
        self.assertEqual(metadata.get('backend_id'), 'aws-sim-sv1')
        self.assertEqual(metadata.get('provider'), 'AWS')
        self.assertEqual(metadata.get('shots'), 1)
        self.assertIsNone(metadata.get('circuit'))
        self.assertIsNone(metadata.get('circuit_type'))
        self.assertEqual(metadata.get('input_params').get('qubit_count'), 2)
        self.assertEqual(metadata.get('input_params').get('disableQubitRewiring'), False)
        self.assertIsNone(metadata.get('begin_execution_time'))
        self.assertIsNone(metadata.get('cancellation_time'))
        self.assertIsNone(metadata.get('error_data'))
        self.assertIsNone(metadata.get('metadata'))
        # This the internal job status name not the Qiskit status name
        self.assertEqual(metadata.get('status'), 'COMPLETED')
        self.assertEqual(metadata.get('tags'), [])

    def test_should_retrieve_job_status(self):
        # Given: create job
        planqk_backend = self.planqk_provider.get_backend("SV1")
        circuit = get_sample_circuit(planqk_backend)
        created_job = planqk_backend.run(circuit, shots=1)

        # When

        # Get job via AWS
        aws_backend = self.braket_provider.get_backend("SV1")
        aws_arn = job_id_to_aws_arn(created_job.job_id())
        exp_job_status = aws_backend.retrieve_job(aws_arn).status()

        # Get job via PlanQK
        job_status = planqk_backend.retrieve_job(created_job.id).status()

        self.assertEqual(exp_job_status, job_status)

    def test_should_retrieve_job_result(self):
        # Given: create job
        planqk_backend = self.planqk_provider.get_backend("SV1")
        circuit = get_sample_circuit(planqk_backend)
        created_job = planqk_backend.run(circuit, shots=10)

        # Get job result via AWS
        aws_backend = self.braket_provider.get_backend("SV1")
        aws_arn = job_id_to_aws_arn(created_job.job_id())
        exp_job = aws_backend.retrieve_job(aws_arn)
        exp_result = exp_job.result()

        # Get job result via PlanQK
        job = planqk_backend.retrieve_job(created_job.id)
        result = job.result()

        self.assertEqual(result.backend_name, planqk_backend.name)
        self.assertEqual(result.backend_version, exp_result.backend_version)
        self.assertEqual(result.qobj_id, exp_result.qobj_id)
        # PlanQK id is different from AWS id since it uses a _ instead of a /
        self.assertEqual(result.job_id, exp_result.job_id.replace('/', '_'))
        self.assertEqual(result.success, exp_result.success)
        self.assertEqual(len(result.results), len(exp_result.results))
        self.assertEqual(result.results[0].shots, exp_result.results[0].shots)
        self.assertEqual(result.results[0].success, exp_result.results[0].success)
        self.assertEqual(result.results[0].meas_level, exp_result.results[0].meas_level)
        self.assertEqual(result.results[0].data.counts, exp_result.results[0].data.counts)
        self.assertEqual(result.results[0].data.memory, exp_result.results[0].data.memory)
        self.assertEqual(result.results[0].status.name, JobStatus.DONE.name)
        self.assertIsNotNone(result.date)
        self.assertEqual(result.status, exp_result.status)
        self.assertEqual(result.header, exp_result.header)

    def test_should_monitor_job(self):
        planqk_backend = self.planqk_provider.get_backend("SV1")
        circuit = get_sample_circuit(planqk_backend)
        created_job = planqk_backend.run(circuit, shots=1)

        # Get job status via PlanQK
        job = planqk_backend.retrieve_job(created_job.job_id())
        sys.stdout = planqk_stdout = StringIO()

        job_monitor(job, output=planqk_stdout)

        console_output = planqk_stdout.getvalue()

        self.assertIn('Job STATUS: job has successfully run', console_output)

    def test_should_cancel_job(self):
        backend = self.planqk_provider.get_backend("Harmony 2")
        circuit = get_sample_circuit(backend)
        planqk_job = backend.run(circuit, shots=1)
        planqk_job.cancel()

        def assert_job_cancelled():
            job_status = planqk_job.status()
            assert job_status.name == JobStatus.CANCELLED.name

        wait().until_asserted(assert_job_cancelled)
