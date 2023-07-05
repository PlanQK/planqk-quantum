"""Util function for provider."""
import json
from typing import Callable, Dict, Optional

from braket.circuits import Circuit, Instruction, gates, result_types
from braket.circuits.compiler_directives import StartVerbatimBox
from braket.circuits.gates import PulseGate
from braket.circuits.serialization import QubitReferenceType, OpenQASMSerializationProperties, IRType
from braket.device_schema import (
    DeviceCapabilities,
)
from braket.ir.openqasm import Program as OpenQASMProgram
from braket.schema_common import BraketSchemaBase
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
qiskit_gate_name_to_planqk_gate_mapping: Dict[str, Optional[QiskitInstruction]] = {
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


def _op_to_instruction(operation: str) -> Optional[QiskitInstruction]:
    """Converts PlanQK operation to Qiskit Instruction.

    Args:
        operation: operation

    Returns:
        Circuit Instruction
    """
    operation = operation.lower()
    return qiskit_gate_name_to_planqk_gate_mapping.get(operation, None)


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
