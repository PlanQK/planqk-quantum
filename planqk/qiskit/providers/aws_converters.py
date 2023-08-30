"""Util function for provider."""
from typing import Callable, Dict, Optional

from braket.circuits import Circuit, Instruction, gates, result_types
from braket.circuits.compiler_directives import StartVerbatimBox
from braket.circuits.gates import PulseGate
from braket.circuits.serialization import QubitReferenceType, OpenQASMSerializationProperties, IRType
from braket.ir.openqasm import Program as OpenQASMProgram
from numpy import pi
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction as QiskitInstruction
from qiskit.circuit import Parameter
from qiskit.circuit.library import (
    CCXGate,
    CPhaseGate,
    CSwapGate,
    CXGate,
    CYGate,
    CZGate,
    ECRGate,
    HGate,
    IGate,
    PhaseGate,
    RXGate,
    RXXGate,
    RYGate,
    RYYGate,
    RZGate,
    RZZGate,
    SdgGate,
    SGate,
    SwapGate,
    SXdgGate,
    SXGate,
    TdgGate,
    TGate,
    U1Gate,
    U2Gate,
    U3Gate,
    XGate,
    YGate,
    ZGate,
)

qiskit_to_braket_gate_names_mapping = {
    "u1": "u1",
    "u2": "u2",
    "u3": "u3",
    "p": "phaseshift",
    "cx": "cnot",
    "x": "x",
    "y": "y",
    "z": "z",
    "t": "t",
    "tdg": "ti",
    "s": "s",
    "sdg": "si",
    "sx": "v",
    "sxdg": "vi",
    "swap": "swap",
    "rx": "rx",
    "ry": "ry",
    "rz": "rz",
    "rzz": "zz",
    "id": "i",
    "h": "h",
    "cy": "cy",
    "cz": "cz",
    "ccx": "ccnot",
    "cswap": "cswap",
    "cp": "cphaseshift",
    "rxx": "xx",
    "ryy": "yy",
    "ecr": "ecr",
}

qiskit_gate_names_to_braket_gates: Dict[str, Callable] = {
    "u1": lambda lam: [gates.Rz(lam)],
    "u2": lambda phi, lam: [gates.Rz(lam), gates.Ry(pi / 2), gates.Rz(phi)],
    "u3": lambda theta, phi, lam: [
        gates.Rz(lam),
        gates.Rx(pi / 2),
        gates.Rz(theta),
        gates.Rx(-pi / 2),
        gates.Rz(phi),
    ],
    "p": lambda angle: [gates.PhaseShift(angle)],
    "cp": lambda angle: [gates.CPhaseShift(angle)],
    "cx": lambda: [gates.CNot()],
    "x": lambda: [gates.X()],
    "y": lambda: [gates.Y()],
    "z": lambda: [gates.Z()],
    "t": lambda: [gates.T()],
    "tdg": lambda: [gates.Ti()],
    "s": lambda: [gates.S()],
    "sdg": lambda: [gates.Si()],
    "sx": lambda: [gates.V()],
    "sxdg": lambda: [gates.Vi()],
    "swap": lambda: [gates.Swap()],
    "rx": lambda angle: [gates.Rx(angle)],
    "ry": lambda angle: [gates.Ry(angle)],
    "rz": lambda angle: [gates.Rz(angle)],
    "rzz": lambda angle: [gates.ZZ(angle)],
    "id": lambda: [gates.I()],
    "h": lambda: [gates.H()],
    "cy": lambda: [gates.CY()],
    "cz": lambda: [gates.CZ()],
    "ccx": lambda: [gates.CCNot()],
    "cswap": lambda: [gates.CSwap()],
    "rxx": lambda angle: [gates.XX(angle)],
    "ryy": lambda angle: [gates.YY(angle)],
    "ecr": lambda: [gates.ECR()],
}

# TODP mark add copyright from braket
qiskit_gate_name_to_braket_gate_mapping: Dict[str, Optional[QiskitInstruction]] = {
    "u1": U1Gate(Parameter("theta")),
    "u2": U2Gate(Parameter("theta"), Parameter("lam")),
    "u3": U3Gate(Parameter("theta"), Parameter("phi"), Parameter("lam")),
    "h": HGate(),
    "ccnot": CCXGate(),
    "cnot": CXGate(),
    "cphaseshift": CPhaseGate(Parameter("theta")),
    "cswap": CSwapGate(),
    "cy": CYGate(),
    "cz": CZGate(),
    "i": IGate(),
    "phaseshift": PhaseGate(Parameter("theta")),
    "rx": RXGate(Parameter("theta")),
    "ry": RYGate(Parameter("theta")),
    "rz": RZGate(Parameter("phi")),
    "s": SGate(),
    "si": SdgGate(),
    "swap": SwapGate(),
    "t": TGate(),
    "ti": TdgGate(),
    "v": SXGate(),
    "vi": SXdgGate(),
    "x": XGate(),
    "xx": RXXGate(Parameter("theta")),
    "y": YGate(),
    "yy": RYYGate(Parameter("theta")),
    "z": ZGate(),
    "zz": RZZGate(Parameter("theta")),
    "ecr": ECRGate(),
}


# TODO metnion copyrigtht
def convert_qiskit_to_planqk_circuit(circuit: QuantumCircuit) -> Circuit:
    """Return a PlanQK quantum input (bases on AWS Braket input) from a Qiskit quantum input.
     Args:
            circuit (QuantumCircuit): PlanQK Quantum Cricuit

    Returns:
        Circuit: PlanQK input
    """
    quantum_circuit = Circuit()
    for qiskit_gates in circuit.data:
        name = qiskit_gates[0].name
        if name == "measure":
            # TODO: change Probability result type for Sample for proper functioning # pylint:disable=fixme
            # Getting the index from the bit mapping
            quantum_circuit.add_result_type(
                result_types.Probability(
                    target=[
                        circuit.find_bit(qiskit_gates[1][0]).index,
                        circuit.find_bit(qiskit_gates[2][0]).index,
                    ]
                )
            )
        elif name == "barrier":
            # This does not exist
            pass
        else:
            params = []
            if hasattr(qiskit_gates[0], "params"):
                params = qiskit_gates[0].params

            for gate in qiskit_gate_names_to_braket_gates[name](*params):
                instruction = Instruction(
                    # Getting the index from the bit mapping
                    operator=gate,
                    target=[circuit.find_bit(i).index for i in qiskit_gates[1]],
                )
                quantum_circuit += instruction
    return quantum_circuit


def wrap_circuit_in_verbatim_box(circuit: Circuit) -> Circuit:
    """Convert Braket input an equivalent one wrapped in verbatim box.

    Args:
           circuit (Circuit): input to be wrapped in verbatim box.
    Returns:
           Circuit wrapped in verbatim box, comprising the same instructions
           as the original one and with result types preserved.
    """
    return Circuit(circuit.result_types).add_verbatim_box(Circuit(circuit.instructions))


def convert_continuous_qubit_indices(connectivity_graph: dict, ) -> dict:
    """
    This function was copied from the following source:
    https://github.com/qiskit-community/qiskit-braket-provider/blob/984101cec132777c2559a41e9fc4f9ef208e391e/qiskit_braket_provider/providers/adapter.py#L306

    Aspen qubit indices are discontinuous (label between x0 and x7, x being
    the number of the octagon) while the Qiskit transpiler creates and/or
    handles coupling maps with continuous indices. This function converts the
    discontinous connectivity graph from Aspen to a continuous one.

    Args:
        connectivity_graph (dict): connectivity graph from Aspen. For example
        4 qubit system, the connectivity graph will be:
            {"0": ["1", "2", "7"], "1": ["0","2","7"], "2": ["0","1","7"],
            "7": ["0","1","2"]}

    Returns:
        dict: Connectivity graph with continuous indices. For example for an
        input connectivity graph with discontinuous indices (qubit 0, 1, 2 and
        then qubit 7) as shown here:
            {"0": ["1", "2", "7"], "1": ["0","2","7"], "2": ["0","1","7"],
            "7": ["0","1","2"]}
        the qubit index 7 will be mapped to qubit index 3 for the qiskit
        transpilation step. Thereby the resultant continous qubit indices
        output will be:
            {"0": ["1", "2", "3"], "1": ["0","2","3"], "2": ["0","1","3"],
            "3": ["0","1","2"]}
    """
    # Creates list of existing qubit indices which are discontinuous.
    indices = [int(key) for key in connectivity_graph.keys()]
    indices.sort()
    # Creates a list of continuous indices for number of qubits.
    map_list = list(range(len(indices)))
    # Creates a dictionary to remap the discountinous indices to continuous.
    mapper = dict(zip(indices, map_list))
    # Performs the remapping from the discontinous to the continuous indices.
    continous_connectivity_graph = {
        mapper[int(k)]: [mapper[int(v)] for v in val]
        for k, val in connectivity_graph.items()
    }
    return continous_connectivity_graph


def transform_to_qasm_3_program(braket_circuit: Circuit,
                                disable_qubit_rewiring: bool,
                                inputs: Dict[str, float]) -> str:
    """Transforms a Braket input to a QASM 3 program."""

    qubit_reference_type = QubitReferenceType.VIRTUAL

    if (
            disable_qubit_rewiring
            or Instruction(StartVerbatimBox()) in braket_circuit.instructions
            or any(isinstance(instruction.operator, PulseGate) for instruction in braket_circuit.instructions)
    ):
        qubit_reference_type = QubitReferenceType.PHYSICAL

    serialization_properties = OpenQASMSerializationProperties(
        qubit_reference_type=qubit_reference_type
    )

    openqasm_program = braket_circuit.to_ir(
        ir_type=IRType.OPENQASM, serialization_properties=serialization_properties
    )
    # TODO do Inputs have a purpose in QASM 3 / qiskit?
    if inputs:
        inputs_copy = openqasm_program.inputs.copy() if openqasm_program.inputs is not None else {}
        inputs_copy.update(inputs)
        openqasm_program = OpenQASMProgram(
            source=openqasm_program.source,
            inputs=inputs_copy,
        )

    return openqasm_program.source
