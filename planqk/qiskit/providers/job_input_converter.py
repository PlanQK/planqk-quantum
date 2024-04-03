import json
from typing import List, Tuple

from braket.circuits import Circuit
from braket.circuits.circuit_helpers import validate_circuit_and_shots
from planqk.qiskit.backend import PlanqkBackend
from planqk.qiskit.client.backend_dtos import PROVIDER
from planqk.qiskit.client.job_dtos import INPUT_FORMAT
from planqk.qiskit.providers.aws_converters import transform_to_qasm_3_program
from planqk.qiskit.providers.qryd.qryd_converters import convert_to_wire_format, create_qoqu_input_params
from qiskit import QuantumCircuit
from qiskit.providers import Options
from qiskit_braket_provider.providers.adapter import to_braket
from qiskit_ibm_runtime import RuntimeEncoder
from qiskit_ionq.helpers import qiskit_circ_to_ionq_circ


def _convert_to_open_qasm_3(circuit: QuantumCircuit, backend: PlanqkBackend, options: Options):
    shots = options.get("shots", 1)
    inputs = options.get("inputs", {})
    verbatim = options.get("verbatim", False)

    basis_gates = backend.operation_names if not verbatim else None
    braket_circuit = to_braket(circuit, basis_gates, verbatim=verbatim)

    validate_circuit_and_shots(braket_circuit, shots)

    return transform_to_qasm_3_program(braket_circuit, False, inputs)


def _convert_to_ionq(circuit: QuantumCircuit, backend: PlanqkBackend, options: Options):
    gateset = options.get("gateset", "qis")
    ionq_circ, _, _ = qiskit_circ_to_ionq_circ(circuit, gateset=gateset)
    return {
        "gateset": gateset,
        "qubits": circuit.num_qubits,
        "circuit": ionq_circ,
    }


def _convert_to_qiskit_primitive(circuit: QuantumCircuit, backend: PlanqkBackend, options: Options):
    # Transforms circuit to base64 encoded byte stream
    input_json_str = json.dumps(circuit, cls=RuntimeEncoder)
    # Transform back to json but with the base64 encoded byte stream
    return json.loads(input_json_str)


def _convert_to_qoqo_circuit(circuit: QuantumCircuit, backend: PlanqkBackend, options: Options):
    return convert_to_wire_format(circuit=circuit, options=options)


def _create_qoqo_input_params(circuit: QuantumCircuit, options: Options):
    return create_qoqu_input_params(circuit=circuit, options=options)


def _create_aws_input_params(circuit: QuantumCircuit, options: Options):
    return {'disable_qubit_rewiring': False}


def _create_empty_input_params(circuit: Circuit, options: Options):
    return {}


input_format_converter_factory = {
    INPUT_FORMAT.OPEN_QASM_V3: _convert_to_open_qasm_3,
    INPUT_FORMAT.IONQ_CIRCUIT_V1: _convert_to_ionq,
    INPUT_FORMAT.QISKIT_PRIMITIVE: _convert_to_qiskit_primitive,
    INPUT_FORMAT.QOQO: _convert_to_qoqo_circuit
}

input_params_factory = {
    PROVIDER.AWS: _create_aws_input_params,
    PROVIDER.QRYD: _create_qoqo_input_params
}


class UnsupportedFormatException(Exception):
    pass


def convert_to_backend_input(supported_input_formats: List[INPUT_FORMAT], circuit, backend=None, options=None) \
        -> Tuple[INPUT_FORMAT, dict]:
    for input_format in supported_input_formats:
        convert_circuit = input_format_converter_factory.get(input_format)
        if convert_circuit:
            return input_format, convert_circuit(circuit=circuit, backend=backend, options=options)
    raise UnsupportedFormatException("Could not convert input to any of the supported inputs formats of the actual")


def convert_to_backend_params(provider: PROVIDER, circuit, options=None) -> dict:
    create_params = input_params_factory.get(provider)
    if create_params:
        return create_params(circuit=circuit, options=options)
    else:
        return {}
