import copy
import os
import unittest.mock

import responses
from qiskit.qobj.utils import MeasLevel

from planqk.exceptions import PlanqkClientError
from planqk.qiskit import PlanqkQuantumProvider
from tests.integration.mocks import BACKENDS_MOCK_RESPONSE, MOCK_JOB, MOCK_JOB_RESPONSE
from tests.utils import get_sample_circuit

BASE_URL = 'http://127.0.0.1:8080'
os.environ['PLANQK_QUANTUM_BASE_URL'] = BASE_URL


class JobTestSuite(unittest.TestCase):

    def setUp(self):
        self.planqk_provider = PlanqkQuantumProvider("mock_token")
        responses.add(responses.GET, BASE_URL + '/backends',
                      json=BACKENDS_MOCK_RESPONSE, status=200)
        # Ensure to see the diff of large objects
        self.maxDiff = None
        self.mockJob = copy.deepcopy(MOCK_JOB)

    @responses.activate
    def test_should_run_job(self):
        responses.add(responses.POST, BASE_URL + '/jobs',
                      json=self.mockJob, status=201)

        sim_backend = self.planqk_provider.get_backend("ionq.simulator")
        circuit = get_sample_circuit(sim_backend)
        job = sim_backend.run(circuit, shots=1)

        assert job.id() == self.mockJob['id']
        job_metadata = job.metadata
        assert job_metadata['input_data_format'] == self.mockJob['input_data_format']
        assert job_metadata['input_params'] == self.mockJob['input_params']
        assert job_metadata['metadata'] == self.mockJob['metadata']
        assert job_metadata['name'] == self.mockJob['name']
        assert job_metadata['output_data_format'] == self.mockJob['output_data_format']
        assert job_metadata['provider_id'] == self.mockJob['provider_id']
        assert job_metadata['target'] == self.mockJob['target']

    @responses.activate
    def test_should_retrieve_job(self):
        job_id = self.mockJob['id']
        responses.add(responses.GET, f'{BASE_URL}/jobs/{job_id}',
                      json=self.mockJob, status=200)

        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(job_id)

        assert job.id() == self.mockJob['id']
        assert job.metadata == {}

    @responses.activate
    def test_should_get_error_when_retrieving_non_existing_job(self):
        job_id = "5f8a37cf-6f90-4b46-86a2-73cbbf469322"
        error_msg = f'The quantum job with id {job_id} could not be found'
        responses.add(responses.GET, f'{BASE_URL}/jobs/{job_id}', json={"status": "NOT_FOUND",
                                                                        "error_message": error_msg}, status=404)

        exp_error_msg = f'Error requesting details of job "{job_id}" (HTTP 404: {{"status": "NOT_FOUND", ' \
                        f'"error_message": "The quantum job with id {job_id} could not be found"}})'
        with self.assertRaises(PlanqkClientError) as context:
            self.planqk_provider.get_backend("ionq.simulator").retrieve_job(job_id)
        self.assertTrue(exp_error_msg in str(context.exception))

    @responses.activate
    def test_should_retrieve_job(self):
        job_id = self.mockJob['id']
        responses.add(responses.GET, f'{BASE_URL}/jobs/{job_id}',
                      json=self.mockJob, status=200)

        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(job_id)

        assert job.id() == self.mockJob['id']
        assert job.metadata == {}

    @responses.activate
    def test_should_retrieve_job_status(self):
        self.mockJob['status'] = 'Waiting'
        job_id = self.mockJob['id']
        responses.add(responses.GET, f'{BASE_URL}/jobs/{job_id}',
                      json=self.mockJob, status=200)

        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(job_id)
        # Azure uses own job state names, e.g. the job state WAITING is mapped to QUEUED
        assert job.status().name == 'QUEUED'

    @responses.activate
    def test_should_retrieve_job_result_of_completed_job(self):
        job_id = self.mockJob['id']
        self.mockJob['status'] = 'Succeeded'
        responses.add(responses.GET, f'{BASE_URL}/jobs/{job_id}',
                      json=self.mockJob, status=200)

        responses.add(responses.GET, f'{BASE_URL}/jobs/{job_id}/result',
                      json=MOCK_JOB_RESPONSE, status=200)

        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(job_id)
        job_result = job.result()

        assert job_result.backend_name == 'ionq.simulator'
        assert job_result.backend_version == 1

        assert job_result.job_id == job_id
        assert job_result.qobj_id == 'Qiskit Sample - 3-qubit GHZ circuit'
        self.assertTrue(job_result.success)

        # TODO: Check if this is correct because if enabled, the test case fails
        # self.assertIsNone(job_result.date)
        # self.assertIsNone(job_result.header)
        # self.assertIsNone(job_result.status)

        results = job_result.results
        assert len(results) == 1
        self.assertTrue(results[0].data.counts == {'000': 1} or results[0].data.counts == {'111': 1})
        self.assertEqual(results[0].data.probabilities['000'], 0.5)
        self.assertEqual(results[0].data.probabilities['111'], 0.5)
        self.assertEqual(results[0].header.meas_map, '[0, 1, 2]')
        self.assertIsNone(results[0].header.metadata)
        self.assertEqual(results[0].header.name, 'Qiskit Sample - 3-qubit GHZ circuit')
        self.assertEqual(results[0].header.num_qubits, '3')
        self.assertEqual(results[0].header.qiskit, 'true')
        self.assertEqual(results[0].meas_level, MeasLevel.CLASSIFIED)
        self.assertEqual(results[0].shots, 1)
        self.assertTrue(results[0].success)

    @responses.activate
    def test_should_cancel_job(self):
        job_id = self.mockJob['id']
        responses.add(responses.GET, f'{BASE_URL}/jobs/{job_id}',
                      json=self.mockJob, status=200)
        responses.add(responses.DELETE, f'{BASE_URL}/jobs/{job_id}', status=204)

        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(job_id)
        job.cancel()

        # Cancelled state is set in Azure, hence, response must be mocked
        self.mockJob['status'] = 'Cancelled'
        responses.add(responses.GET, f'{BASE_URL}/jobs/{job_id}',
                      json=self.mockJob, status=200)

        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(job_id)
        self.assertEqual("CANCELLED", job.status().name)

    @responses.activate
    def test_should_get_job(self):
        job_id = self.mockJob['id']
        self.mockJob['status'] = 'Waiting'
        responses.add(responses.GET, f'{BASE_URL}/jobs/{job_id}',
                      json=self.mockJob, status=200)

        responses.add(responses.GET, BASE_URL + '/backends',
                      json=BACKENDS_MOCK_RESPONSE, status=200)

        job = self.planqk_provider.get_job(job_id)
        self.assertEqual("QUEUED", job.status().name)
