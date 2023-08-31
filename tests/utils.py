from uuid import UUID

from qiskit import QuantumCircuit
from qiskit.circuit.library import RealAmplitudes
from qiskit.quantum_info import SparsePauliOp


def get_sample_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(3, 3)
    circuit.name = "Qiskit Sample - 3-qubit GHZ input"
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)
    circuit.measure([0, 1, 2], [0, 1, 2])

    return circuit


def get_estimator_circuit():
    psi = RealAmplitudes(num_qubits=2, reps=2)

    h1 = SparsePauliOp.from_list([("IZ", 1)])
    h2 = SparsePauliOp.from_list([("ZI", 1), ("ZZ", 1)])

    theta = [0, 1, 1, 2, 3, 5]

    return {
        'circuits': [psi, psi],
        'observables': [h1, h2],
        'parameter_values': [theta] * 2
    }


SAMPLE_CIRCUIT_HARMONY_TRANSPILATION_RESULT = """global phase: 3π/2
                ┌──────────┐┌────────┐          ┌─┐      
       q_0 -> 0 ┤ Ry(-π/2) ├┤ Rz(-π) ├──■───────┤M├──────
                └──────────┘└────────┘┌─┴─┐     └╥┘┌─┐   
       q_1 -> 1 ──────────────────────┤ X ├──■───╫─┤M├───
                                      └───┘┌─┴─┐ ║ └╥┘┌─┐
       q_2 -> 2 ───────────────────────────┤ X ├─╫──╫─┤M├
                                           └───┘ ║  ║ └╥┘
 ancilla_0 -> 3 ─────────────────────────────────╫──╫──╫─
                                                 ║  ║  ║ 
 ancilla_1 -> 4 ─────────────────────────────────╫──╫──╫─
                                                 ║  ║  ║ 
 ancilla_2 -> 5 ─────────────────────────────────╫──╫──╫─
                                                 ║  ║  ║ 
 ancilla_3 -> 6 ─────────────────────────────────╫──╫──╫─
                                                 ║  ║  ║ 
 ancilla_4 -> 7 ─────────────────────────────────╫──╫──╫─
                                                 ║  ║  ║ 
 ancilla_5 -> 8 ─────────────────────────────────╫──╫──╫─
                                                 ║  ║  ║ 
 ancilla_6 -> 9 ─────────────────────────────────╫──╫──╫─
                                                 ║  ║  ║ 
ancilla_7 -> 10 ─────────────────────────────────╫──╫──╫─
                                                 ║  ║  ║ 
           c: 3/═════════════════════════════════╩══╩══╩═
                                                 0  1  2 """


def get_width_sample_circuit(n_bits: int) -> QuantumCircuit:
    circuit = QuantumCircuit(n_bits, n_bits)
    circuit.h(range(n_bits))

    # perform measurement
    circuit.measure(range(n_bits), range(n_bits))

    return circuit


def is_valid_uuid(uuid_to_test):
    try:
        UUID(str(uuid_to_test))
    except ValueError:
        return False
    return True


def to_dict(obj):
    if not hasattr(obj, "__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        element = []
        if isinstance(val, list):
            for item in val:
                element.append(to_dict(item))
        else:
            element = to_dict(val)
        result[key] = element
    return result


def transform_decimal_to_bitsrings(data: dict[str, int], num_qubits: int) -> dict[str, int]:
    updated_data: dict[str, int] = {}
    for key, value in data.items():
        bitstring_key = transform_decimal_to_bitstring(key, num_qubits)
        updated_data[bitstring_key] = value

    return updated_data


def transform_decimal_to_bitstring(decimal_str: str, num_qubits):
    # Convert number to bit string
    bit_string = bin(int(decimal_str))[2:].zfill(num_qubits)
    return bit_string[::-1]
