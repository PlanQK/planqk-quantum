BACKENDS_MOCK_RESPONSE = {
    "value": [
        {
            "id": "ionq",
            "current_availability": "Available",
            "targets": [
                {
                    "id":
                        "ionq.qpu", "current_availability":
                    "Available", "average_queue_time": 87742,
                    "status_page": "https://status.ionq.co"
                },
                {
                    "id": "ionq.qpu.aria-1",
                    "current_availability": "Available",
                    "average_queue_time": 283143,
                    "status_page": "https://status.ionq.co"
                },
                {
                    "id": "ionq.simulator",
                    "current_availability": "Available",
                    "average_queue_time": 2,
                    "status_page": "https://status.ionq.co"
                }
            ]
        },
        {
            "id": "rigetti",
            "current_availability": "Degraded",
            "targets": [
                {
                    "id": "rigetti.sim.qvm",
                    "current_availability": "Available",
                    "average_queue_time": 5,
                    "status_page": "https://rigetti.statuspage.io/"
                },
                {
                    "id": "rigetti.qpu.aspen-11",
                    "current_availability": "Unavailable",
                    "average_queue_time": 0},
                {
                    "id": "rigetti.qpu.aspen-m-2",
                    "current_availability": "Available",
                    "average_queue_time": 5,
                    "status_page": "https://rigetti.statuspage.io/"},
                {
                    "id": "rigetti.qpu.aspen-m-3",
                    "current_availability": "Available",
                    "average_queue_time": 5,
                    "status_page": "https://rigetti.statuspage.io/"
                }
            ]
        }
    ]
}

BACKEND_IONQ_MOCK_CONFIG = {
    'backend_name': 'ionq.qpu',
    'backend_version': '0.24.208024',
    'n_qubits': 11,
    'basis_gates': ['ccx', 'ch', 'cnot', 'cp', 'crx', 'cry', 'crz', 'csx', 'cx', 'cy', 'cz',
                    'h', 'i', 'id', 'mcp', 'mcphase', 'mct', 'mcx', 'mcx_gray', 'measure', 'p',
                    'rx', 'rxx', 'ry', 'ryy', 'rz', 'rzz', 's', 'sdg', 'swap', 'sx', 'sxdg',
                    't', 'tdg', 'toffoli', 'x', 'y', 'z'],
    'gates': [{'name': 'TODO', 'parameters': [], 'qasm_def': 'TODO'}],
    'local': False,
    'simulator': False,
    'conditional': False,
    'open_pulse': False,
    'memory': False,
    'max_shots': 10000,
    'coupling_map': None,
    'dynamic_reprate_enabled': False,
    'max_experiments': 1, 'description': 'IonQ QPU on Azure Quantum'
}

BACKEND_IONQ_MOCK_STATUS = {
    'backend_name': 'ionq.qpu',
    'backend_version': '1',
    'operational': True,
    'pending_jobs': 0,
    'status_msg': ''
}

MOCK_JOB = {
    'id': '66ab14a8-62ec-40ac-89f7-266cb9bc52b0',
    'creation_time': '2022-12-29T17:43:49.6738189+00:00',
    'input_params': {'shots': 1},
    'input_data_format': 'ionq.circuit.v1',
    'metadata': {
        'metadata': 'null',
        'num_qubits': '3',
        'name': 'Qiskit Sample - 3-qubit GHZ circuit',
        'qiskit': 'true',
        'meas_map': '[0, 1, 2]',
    },
    'name': 'Qiskit Sample - 3-qubit GHZ circuit',
    'output_data_format': 'ionq.quantum-results.v1',
    'provider_id': 'ionq',
    'status': 'Waiting',
    'target': 'ionq.simulator',
    'tags': []
}

MOCK_JOB_RESPONSE = {'histogram': {'0': 0.5, '7': 0.5}}

MOCK_JOB_RESULT = {
    'backend_name': 'ionq.simulator',
    'backend_version': 1,
    'qobj_id': 'Qiskit Sample - 3-qubit GHZ circuit',
    'job_id': '66ab14a8-62ec-40ac-89f7-266cb9bc52b0',
    'success': True,
    'results': [
        {
            'shots': 1,
            'success': True,
            'data': {'probabilities': {'000': 0.5, '111': 0.5}},
            'meas_level': {},
            'header': {
                'qiskit': 'true',
                'name': 'Qiskit Sample - 3-qubit GHZ circuit',
                'num_qubits': '3',
                'metadata': None, 'meas_map': '[0, 1, 2]'
            }
        }
    ],
    'date': None,
    'status': None,
    'header': None
}
