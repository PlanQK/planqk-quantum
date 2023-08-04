import unittest
from unittest.mock import patch, MagicMock, Mock

from requests import HTTPError

from planqk.exceptions import InvalidAccessTokenError, PlanqkClientError
from planqk.qiskit.client.backend_dtos import BackendDto, PROVIDER
from planqk.qiskit.client.client import _PlanqkClient
from planqk.qiskit.client.job_dtos import JobDto
from tests.unit.planqk.client_mocks import rigetti_mock, oqc_lucy_mock, job_mock, job_result_mock


class TestPlanqkClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._original_get_default_headers = _PlanqkClient._get_default_headers

        # Override _get_default_headers to always return a specific token
        _PlanqkClient._get_default_headers = MagicMock(return_value={"x-auth-token": "test_token"})

    @patch("requests.get")
    def test_get_backends(self, mock_get):
        # Given
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [rigetti_mock, oqc_lucy_mock]

        # When
        result = _PlanqkClient.get_backends()

        # Then
        self.assertEqual(2, len(result))
        self.assert_backend(rigetti_mock, result[0])
        self.assert_backend(oqc_lucy_mock, result[1])

    @patch("requests.get")
    def test_get_backend(self, mock_get):
        # Given
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = rigetti_mock

        # When
        result = _PlanqkClient.get_backend(rigetti_mock["id"])

        # Then
        self.assert_backend(rigetti_mock, result)

    @patch("requests.post")
    def test_submit_job(self, mock_post):
        # Give
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": "123"}

        # When
        job = JobDto(rigetti_mock["id"], PROVIDER.AWS.name)
        job_id = _PlanqkClient.submit_job(job)

        # Then
        self.assertEqual("123", job_id)

    @patch("requests.get")
    def test_get_job(self, mock_get):
        # Given
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = job_mock

        # When
        job = _PlanqkClient.get_job("123", None)

        # Then
        self.assertEqual(job_mock["backend_id"], job.backend_id)
        self.assertEqual(job_mock["provider"], job.provider)
        self.assertEqual(job_mock["shots"], job.shots)
        self.assertEqual(job_mock["id"], job.id)
        self.assertDictEqual(job_mock["input"], job.input)
        self.assertEqual(job_mock["input_format"], job.input_format)
        self.assertDictEqual(job_mock["input_params"], job.input_params)
        self.assertEqual(job_mock["begin_execution_time"], job.begin_execution_time)
        self.assertEqual(job_mock["cancellation_time"], job.cancellation_time)
        self.assertEqual(job_mock["creation_time"], job.creation_time)
        self.assertEqual(job_mock["end_execution_time"], job.end_execution_time)
        self.assertDictEqual(job_mock["error_data"], job.error_data)
        self.assertDictEqual(job_mock["metadata"], job.metadata)
        self.assertEqual(job_mock["name"], job.name)
        self.assertEqual(job_mock["status"], job.status)
        self.assertSetEqual(job_mock["tags"], job.tags)

    @patch("requests.get")
    def test_get_job_result(self, mock_get):
        # Given
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = job_result_mock

        # When
        result = _PlanqkClient.get_job_result("123")

        # Then
        for key, value in result.counts.items():
            self.assertEqual(job_result_mock["counts"][key], value)

        for i, value in enumerate(result.memory):
            self.assertEqual(job_result_mock["memory"][i], value)

    @patch("requests.delete")
    def test_cancel_job(self, mock_delete):
        # Given
        mock_delete.return_value.status_code = 204

        # When
        _PlanqkClient.cancel_job("123")

        # No exception means success

    @patch("requests.get")
    def test_invalid_token(self, mock_get):
        # Given
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {""}
        mock_response.raise_for_status.side_effect = HTTPError("Error", response=mock_response)

        mock_get.return_value = mock_response

        # When
        with self.assertRaises(InvalidAccessTokenError) as error_response:
            _PlanqkClient.get_backend("123")

        # Then
        self.assertEqual(error_response.exception.message, "Invalid personal access token provided.")

    @patch("requests.get")
    def test_planqk_client_error(self, mock_get):
        # Given
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "{\"status\": 404,  \"error_message\": \"The backend with id 123 could not be found\"}"
        mock_response.raise_for_status.side_effect = HTTPError("Error", response=mock_response)

        mock_get.return_value = mock_response

        # When
        with self.assertRaises(PlanqkClientError) as error_response:
            _PlanqkClient.get_backend("123")

        # Then
        self.assertEqual(str(error_response.exception),
                         "The backend with id 123 could not be found (HTTP error: 404)")


    def assert_backend(self, expected: dict, actual: BackendDto):
        # main attributes
        self.assertEqual(expected["id"], actual.id)
        self.assertEqual(expected["internal_id"], actual.internal_id)
        self.assertEqual(expected["provider"], actual.provider.value)
        self.assertEqual(expected["hardware_provider"], actual.hardware_provider.value)
        self.assertEqual(expected["name"], actual.name)
        self.assertEqual(expected["type"], actual.type.value)
        self.assertEqual(expected["status"], actual.status.value)
        self.assertEqual(expected["avg_queue_time"], actual.avg_queue_time)

        # documentation
        doc = expected["documentation"]
        self.assertEqual(doc["description"], actual.documentation.description)
        self.assertEqual(doc["url"], actual.documentation.url)
        self.assertEqual(doc["location"], actual.documentation.location)

        # configuration
        config = expected["configuration"]
        self.assertEqual(len(config["gates"]), len(actual.configuration.gates))
        self.assertEqual(len(config["qubits"]), len(actual.configuration.qubits))
        self.assertEqual(config["qubit_count"], actual.configuration.qubit_count)
        self.assertEqual(config["connectivity"]["fully_connected"], actual.configuration.connectivity.fully_connected)
        self.assertEqual(config["supported_input_formats"][0], actual.configuration.supported_input_formats[0].value)
        self.assertEqual(config["shots_range"]["min"], actual.configuration.shots_range.min)
        self.assertEqual(config["shots_range"]["max"], actual.configuration.shots_range.max)
        self.assertEqual(config["memory_result_returned"], actual.configuration.memory_result_returned)

        # gates
        for gate_mock, gate in zip(config["gates"], actual.configuration.gates):
            self.assertEqual(gate_mock["name"], gate.name)
            self.assertEqual(gate_mock["native"], gate.native)

        # qubits
        for qubit_mock, qubit in zip(config["qubits"], actual.configuration.qubits):
            self.assertEqual(qubit_mock["id"], qubit.id)

        # availability
        for times_mock, times in zip(expected["availability"], actual.availability):
            self.assertEqual(times_mock["granularity"], times.granularity)
            self.assertEqual(times_mock["start"], str(times.start))
            self.assertEqual(times_mock["end"], str(times.end))

        # costs
        for cost_mock, cost in zip(expected["costs"], actual.costs):
            self.assertEqual(cost_mock["granularity"], cost.granularity)
            self.assertEqual(cost_mock["currency"], cost.currency)
            self.assertEqual(cost_mock["value"], cost.value)
