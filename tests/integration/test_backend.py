import os
import unittest.mock

import responses

from planqk.exceptions import PlanqkClientError
from planqk.qiskit.provider import PlanqkQuantumProvider
from tests.integration.mocks import BACKENDS_MOCK_RESPONSE, BACKEND_IONQ_MOCK_CONFIG, BACKEND_IONQ_MOCK_STATUS

BASE_URL = 'http://127.0.0.1:8080'
os.environ['PLANQK_QUANTUM_BASE_URL'] = BASE_URL


class BackendTestSuite(unittest.TestCase):

    def setUp(self):
        self.planqk_provider = PlanqkQuantumProvider(
            "mock_token")

    @responses.activate
    def test_should_list_all_backends(self):
        responses.add(responses.GET, BASE_URL + '/backends',
                      json=BACKENDS_MOCK_RESPONSE, status=200)

        backend_names = []
        for backend in self.planqk_provider.backends():
            backend_names.append(backend.name())

        assert len(backend_names) == 2
        assert backend_names[0] == 'ionq.qpu'
        assert backend_names[1] == 'ionq.simulator'

    @responses.activate
    def test_should_get_backend(self):
        responses.add(responses.GET, BASE_URL + '/backends',
                      json=BACKENDS_MOCK_RESPONSE, status=200)

        backend = self.planqk_provider.get_backend("ionq.qpu")

        assert backend.name() == "ionq.qpu"
        assert backend.backend_name is None
        assert set(backend.backend_names) == set(["ionq.qpu"])

        config = backend.configuration()
        assert config.backend_name == BACKEND_IONQ_MOCK_CONFIG['backend_name']
        assert config.backend_version == BACKEND_IONQ_MOCK_CONFIG['backend_version']
        assert config.basis_gates == BACKEND_IONQ_MOCK_CONFIG['basis_gates']
        assert config.conditional == BACKEND_IONQ_MOCK_CONFIG['conditional']
        assert config.coupling_map == BACKEND_IONQ_MOCK_CONFIG['coupling_map']
        assert config.description == BACKEND_IONQ_MOCK_CONFIG['description']
        assert config.dynamic_reprate_enabled == BACKEND_IONQ_MOCK_CONFIG['dynamic_reprate_enabled']
        assert vars(config.gates[0]) == BACKEND_IONQ_MOCK_CONFIG['gates'][0]
        assert config.local == BACKEND_IONQ_MOCK_CONFIG['local']
        assert config.max_experiments == BACKEND_IONQ_MOCK_CONFIG['max_experiments']
        assert config.max_shots == BACKEND_IONQ_MOCK_CONFIG['max_shots']
        assert config.memory == BACKEND_IONQ_MOCK_CONFIG['memory']
        assert config.n_qubits == BACKEND_IONQ_MOCK_CONFIG['n_qubits']
        assert config.num_qubits == BACKEND_IONQ_MOCK_CONFIG['n_qubits']
        assert config.open_pulse == BACKEND_IONQ_MOCK_CONFIG['open_pulse']
        assert config.simulator == BACKEND_IONQ_MOCK_CONFIG['simulator']

        assert backend.options.shots == 500
        assert vars(backend.status()) == BACKEND_IONQ_MOCK_STATUS
        assert backend.version == 1

    @responses.activate
    def test_should_get_invalid_token_error(self):
        responses.add(responses.GET, BASE_URL + '/backends',
                      json=BACKENDS_MOCK_RESPONSE, status=401)

        with self.assertRaises(PlanqkClientError):
            self.planqk_provider.get_backend("ionq.qpu")
