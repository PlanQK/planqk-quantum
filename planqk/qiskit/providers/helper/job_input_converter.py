from typing import List

from azure.quantum.target import IonQ
from braket.circuits import Circuit
from qiskit_ionq.helpers import qiskit_circ_to_ionq_circ

from planqk.qiskit.client.client_dtos import INPUT_FORMAT


def _convert_to_open_qasm_3(circuit: Circuit):
    pass


def _convert_to_ionq(circuit: Circuit):
    ionq_circ, _, _ = qiskit_circ_to_ionq_circ(circuit)

    input_data = {
        "qubits": circuit.num_qubits,
        "circuit": ionq_circ,
    }

    return IonQ._encode_input_data(input_data)


input_format_converter_factory = {
    INPUT_FORMAT.OPEN_QASM_3: _convert_to_open_qasm_3,
    INPUT_FORMAT.IONQ: _convert_to_ionq,
}

class UnsupportedFormatException(Exception):
    pass


def convert_circuit_to_backend_input(supported_input_formats: List[INPUT_FORMAT], circuit: Circuit):
    for convert_type in supported_input_formats:
        convert_circuit = input_format_converter_factory.get(convert_type)
        if convert_circuit:
            return convert_circuit(circuit)
    raise UnsupportedFormatException("Could not convert circuit "
                                     "to any of the supported inputs formats of the backend")


