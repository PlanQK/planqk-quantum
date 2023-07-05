import json
from typing import List, Tuple

from azure.quantum.target import IonQ
from braket.circuits import Circuit
from braket.circuits.circuit_helpers import validate_circuit_and_shots
from qiskit_braket_provider.providers.adapter import convert_qiskit_to_braket_circuit, wrap_circuits_in_verbatim_box
from qiskit_ionq.helpers import qiskit_circ_to_ionq_circ

from planqk.qiskit.client.client_dtos import INPUT_FORMAT
from planqk.qiskit.providers.helper.adapter import transform_to_qasm_3_program


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


def _convert_to_ionq(circuit: Circuit):
    ionq_circ, _, _ = qiskit_circ_to_ionq_circ(circuit)
    # TODO transpiled input?
    input_data = {
        "qubits": circuit.num_qubits,
        "circuit": ionq_circ,
    }

    # Transform byte json to string json
    return input_data


input_format_converter_factory = {
    INPUT_FORMAT.OPEN_QASM_V3: _convert_to_open_qasm_3,
    INPUT_FORMAT.IONQ_CIRCUIT_V1: _convert_to_ionq,
}


class UnsupportedFormatException(Exception):
    pass


def convert_circuit_to_backend_input(supported_input_formats: List[INPUT_FORMAT], circuit: Circuit) -> Tuple[
    INPUT_FORMAT, dict]:
    for input_format in supported_input_formats:
        convert_circuit = input_format_converter_factory.get(input_format)
        if convert_circuit:
            return input_format, convert_circuit(circuit)
    raise UnsupportedFormatException("Could not convert input "
                                     "to any of the supported inputs formats of the backend")
