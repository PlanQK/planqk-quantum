import json
from typing import List, Tuple

from braket.circuits import Circuit
from braket.circuits.circuit_helpers import validate_circuit_and_shots
from qiskit.providers import Options
from qiskit_braket_provider.providers.adapter import convert_qiskit_to_braket_circuit, wrap_circuits_in_verbatim_box
from qiskit_ibm_runtime import RuntimeEncoder
from qiskit_ionq.helpers import qiskit_circ_to_ionq_circ

from planqk.qiskit.client.job_dtos import INPUT_FORMAT
from planqk.qiskit.providers.aws_converters import transform_to_qasm_3_program
from planqk.qiskit.providers.qryd.qryd_converters import convert_to_wire_format, create_qoqu_input_params


def _convert_to_open_qasm_3(circuit: Circuit, **kwargs):
    braket_circuit = convert_qiskit_to_braket_circuit(circuit)
    shots = kwargs.get("shots", 1)  # TODO default value
    validate_circuit_and_shots(braket_circuit, shots)

    if kwargs.pop("verbatim", False):
        braket_circuit = wrap_circuits_in_verbatim_box(braket_circuit)
    inputs = kwargs.get("inputs", {})

    # TODO quibit rewiring
    qasm_circuit = transform_to_qasm_3_program(braket_circuit, False, inputs)
    return qasm_circuit


def _convert_to_ionq(circuit: Circuit, options: Options):
    ionq_circ, _, _ = qiskit_circ_to_ionq_circ(circuit)
    # TODO transpiled input?
    input_data = {
        "qubits": circuit.num_qubits,
        "circuit": ionq_circ,
    }

    # Transform byte json to string json
    return input_data


def _convert_to_qiskit_primitive(circuit: Circuit, options: Options):
    # Transforms circuit to base64 encoded byte stream
    input_json_str = json.dumps(circuit, cls=RuntimeEncoder)
    # Transform back to json but with the base64 encoded byte stream
    return json.loads(input_json_str)


def _convert_to_qoqo_circuit(circuit: Circuit, options: Options):
    return convert_to_wire_format(circuit=circuit, options=options)


def _create_qoqo_input_params(circuit: Circuit, options: Options):
    return create_qoqu_input_params(circuit=circuit, options=options)


def _create_empty_input_params(circuit: Circuit, options: Options):
    # TODO this is braket specific
    return {'disable_qubit_rewiring': False,
            'qubit_count': circuit.num_qubits}


input_format_converter_factory = {
    INPUT_FORMAT.OPEN_QASM_V3: _convert_to_open_qasm_3,
    INPUT_FORMAT.IONQ_CIRCUIT_V1: _convert_to_ionq,
    INPUT_FORMAT.QISKIT_PRIMITIVE: _convert_to_qiskit_primitive,
    INPUT_FORMAT.QOQO: _convert_to_qoqo_circuit
}

input_params_factory = {
    INPUT_FORMAT.OPEN_QASM_V3: _create_empty_input_params,
    INPUT_FORMAT.IONQ_CIRCUIT_V1: _create_empty_input_params,
    INPUT_FORMAT.QISKIT_PRIMITIVE: _create_empty_input_params,
    INPUT_FORMAT.QOQO: _create_qoqo_input_params
}


class UnsupportedFormatException(Exception):
    pass


def convert_to_backend_input(supported_input_formats: List[INPUT_FORMAT], circuit, options=None) -> Tuple[
    INPUT_FORMAT, dict]:
    for input_format in supported_input_formats:
        convert_circuit = input_format_converter_factory.get(input_format)
        create_input_params = input_params_factory.get(input_format)
        if convert_circuit:
            return input_format, convert_circuit(circuit=circuit, options=options), create_input_params(circuit=circuit,
                                                                                                        options=options)
    raise UnsupportedFormatException("Could not convert input "
                                     "to any of the supported inputs formats of the actual")
