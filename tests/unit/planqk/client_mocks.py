rigetti_mock = {
    "id": "aws.rigetti.aspen",
    "internal_id": "mock_internal_id_1",
    "provider": "AWS",
    "hardware_provider": "RIGETTI",
    "name": "mock_backend_1",
    "documentation": {
        "description": "Mock actual 1",
        "url": "http://mock_url.com",
        "location": "Germany"
    },
    "configuration": {
        "gates": [
            {"name": "gate1", "native_gate": True},
            {"name": "gate2", "native_gate": False}
        ],
        "instructions": ["gate1", "gate2"],
        "qubits": [
            {"id": "qubit1"},
            {"id": "qubit2"}
        ],
        "qubit_count": 2,
        "connectivity": {
            "fully_connected": True,
            "graph": {},
        },
        "supported_input_formats": ["OPEN_QASM_V3"],
        "shots_range": {
            "min": 1,
            "max": 10
        },
        "memory_result_supported": True
    },
    "type": "QPU",
    "status": "ONLINE",
    "availability": [
        {"granularity": "daily", "start": "00:00:00", "end": "23:59:59"},
        {"granularity": "daily", "start": "00:00:00", "end": "23:59:59"}
    ],
    "costs": [
        {"granularity": "shot", "currency": "USD", "value": 0.01},
        {"granularity": "job", "currency": "USD", "value": 1.00}
    ],
    "updated_at": "2023-07-11",
    "avg_queue_time": 10,
    "unknown_attr": "yes",
}

oqc_lucy_mock = {
    "id": "aws.oqc.lucy",
    "internal_id": "mock_internal_id_2",
    "provider": "AWS",
    "hardware_provider": "OQC",
    "name": "mock_backend_2",
    "documentation": {
        "description": "Mock actual 2",
        "url": "http://mock_url_2.com",
        "location": "England"
    },
    "configuration": {
        "gates": [
            {"name": "gate3", "native_gate": True},
            {"name": "gate4", "native_gate": False}
        ],
        "instructions": ["gate3", "gate4"],
        "qubits": [
            {"id": "qubit3"},
            {"id": "qubit4"}
        ],
        "qubit_count": 4,
        "connectivity": {
            "fully_connected": False,
            "graph": {},
        },
        "supported_input_formats": ["OPEN_QASM_V3"],
        "shots_range": {
            "min": 2,
            "max": 20
        },
        "memory_result_supported": False
    },
    "type": "SIMULATOR",
    "status": "OFFLINE",
    "availability": [
        {"granularity": "weekly", "start": "00:00:00", "end": "23:59:59"},
        {"granularity": "weekly", "start": "00:00:00", "end": "23:59:59"}
    ],
    "costs": [
        {"granularity": "job", "currency": "EUR", "value": 0.02},
        {"granularity": "shot", "currency": "EUR", "value": 2.00}
    ],
    "updated_at": "2023-07-12",
    "avg_queue_time": 20
}

job_mock = {
    "backend_id": "aws.rigetti.aspen",
    "provider": "AWS",
    "shots": 10,
    "id": "123",
    "input": {"param1": "value1", "param2": "value2"},
    "input_format": "OPEN_QASM_V3",
    "input_params": {"param1": "value1", "param2": "value2"},
    "begin_execution_time": "2023-07-11T10:00:00",
    "cancellation_time": "2023-07-11T11:00:00",
    "creation_time": "2023-07-11T09:00:00",
    "end_execution_time": "2023-07-11T12:00:00",
    "error_data": {"error_type": "mock_error_type", "error_message": "mock_error_message"},
    "metadata": {"metadata1": "value1", "metadata2": "value2"},
    "name": "mock_job_1",
    "status": "COMPLETED",
    "unknown_attr": "yes",
    "tags": {"tag1", "tag2"}
}

job_result_mock = {
    "counts": {
        "100": 2,
        "111": 1,
    },
    "memory": [
        "100",
        "111",
        "100",
        "111"
    ]
}
