"""Util function for provider."""
from typing import Dict

from braket.circuits import Circuit, Instruction
from braket.circuits.compiler_directives import StartVerbatimBox
from braket.circuits.gates import PulseGate
from braket.circuits.serialization import QubitReferenceType, OpenQASMSerializationProperties, IRType
from braket.ir.openqasm import Program as OpenQASMProgram


def transform_braket_to_qasm_3_program(braket_circuit: Circuit,
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
    if inputs:
        inputs_copy = openqasm_program.inputs.copy() if openqasm_program.inputs is not None else {}
        inputs_copy.update(inputs)
        openqasm_program = OpenQASMProgram(
            source=openqasm_program.source,
            inputs=inputs_copy,
        )

    return openqasm_program.source
