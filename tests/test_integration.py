import os
import unittest
import unittest.mock
import unittest.mock
from unittest import mock

import responses

from planqk.qiskit import PlanqkQuantumProvider

BASE_URL = 'http://127.0.0.1:8080'
os.environ['PLANQK_QUANTUM_BASE_URL'] = BASE_URL

BACKENDS_MOCK_RESPONSE = {"value": [{"id": "ionq", "current_availability": "Available", "targets": [
        {"id": "ionq.qpu", "current_availability": "Available", "average_queue_time": 87742,
         "status_page": "https://status.ionq.co"},
        {"id": "ionq.qpu.aria-1", "current_availability": "Available", "average_queue_time": 283143,
         "status_page": "https://status.ionq.co"},
        {"id": "ionq.simulator", "current_availability": "Available", "average_queue_time": 2,
         "status_page": "https://status.ionq.co"}]}, {"id": "rigetti", "current_availability": "Degraded", "targets": [
        {"id": "rigetti.sim.qvm", "current_availability": "Available", "average_queue_time": 5,
         "status_page": "https://rigetti.statuspage.io/"},
        {"id": "rigetti.qpu.aspen-11", "current_availability": "Unavailable", "average_queue_time": 0},
        {"id": "rigetti.qpu.aspen-m-2", "current_availability": "Available", "average_queue_time": 5,
         "status_page": "https://rigetti.statuspage.io/"},
        {"id": "rigetti.qpu.aspen-m-3", "current_availability": "Available", "average_queue_time": 5,
         "status_page": "https://rigetti.statuspage.io/"}]}]}

BACKEND_IONQ_MOCK_STATUS = {'backend_name': 'ionq.qpu', 'backend_version': '1', 'operational': True, 'pending_jobs': 0, 'status_msg': ''}

BACKEND_IONQ_MOCK_CONFIG = {'backend_name': 'ionq.qpu', 'backend_version': '0.24.208024', 'n_qubits': 11, 'basis_gates': ['ccx', 'ch', 'cnot', 'cp', 'crx', 'cry', 'crz', 'csx', 'cx', 'cy', 'cz', 'h', 'i', 'id', 'mcp', 'mcphase', 'mct', 'mcx', 'mcx_gray', 'measure', 'p', 'rx', 'rxx', 'ry', 'ryy', 'rz', 'rzz', 's', 'sdg', 'swap', 'sx', 'sxdg', 't', 'tdg', 'toffoli', 'x', 'y', 'z'], 'gates': [{'name': 'TODO', 'parameters': [], 'qasm_def': 'TODO'}], 'local': False, 'simulator': False, 'conditional': False, 'open_pulse': False, 'memory': False, 'max_shots': 10000, 'coupling_map': None, 'dynamic_reprate_enabled': False, 'max_experiments': 1, 'description': 'IonQ QPU on Azure Quantum'}
class IntegrationTestSuite(unittest.TestCase):

    def setUp(self):
        self.planqk_provider = PlanqkQuantumProvider(
            "716365ea163a89638d9534721b844528ea3beaa65d147317b0855c4a5b3ad1b22b4723ab86c00a50")

    @responses.activate
    def test_should_list_all_backends(self):

        responses.add(responses.GET, BASE_URL + '/backends',
                      json=BACKENDS_MOCK_RESPONSE, status=200)

        backend_names = []
        for backend in self.planqk_provider.backends():
            backend_names.append(backend.name())

        assert len(backend_names) == 1
        assert backend_names[0] == 'ionq'


    def test_should_get_backend(self):
        responses.add(responses.GET, BASE_URL + '/backends',
                      json=BACKENDS_MOCK_RESPONSE, status=200)

        backend = self.planqk_provider.get_backend("ionq.qpu")

        assert backend.name() == "ionq.qpu"
        assert backend.backend_name is None
        assert set(backend.backend_names) == set(["ionq.qpu"])
        config = vars(backend.configuration())
        del config['_data']
        assert config == BACKEND_IONQ_MOCK_CONFIG #TODO assert json
        assert backend.options.shots == 500
        assert vars(backend.status()) == BACKEND_IONQ_MOCK_STATUS
        assert backend.version == 1




