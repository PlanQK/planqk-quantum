from typing import Optional, List

from qiskit.circuit import Gate, IfElseOp, WhileLoopOp, ForLoopOp, SwitchCaseOp, Instruction
from qiskit.circuit import Parameter, Reset
from qiskit.circuit.library import IGate, SXGate, XGate, CXGate, RZGate, ECRGate, CZGate

from planqk.qiskit.client.backend_dtos import QubitDto, ConnectivityDto
from planqk.qiskit.providers.adapter import ProviderAdapter

ibm_name_mapping = {
    "id": IGate(),
    "sx": SXGate(),
    "x": XGate(),
    "cx": CXGate(),
    "rz": RZGate(Parameter("λ")),
    "reset": Reset(),
    "ecr": ECRGate(),
    "cz": CZGate(),
}

qiskit_control_flow_mapping = {
    "if_else": IfElseOp,
    "while_loop": WhileLoopOp,
    "for_loop": ForLoopOp,
    "switch_case": SwitchCaseOp,
}


class IbmAdapter(ProviderAdapter):

    def to_gate(self, name: str, is_simulator: bool = False) -> Optional[Gate]:
        name = name.lower()

        return ibm_name_mapping.get(name, None) or Gate(name, 0, [])

    def to_non_gate_instruction(self, name: str, is_simulator: bool = False) -> Optional[Instruction]:
        if name in qiskit_control_flow_mapping:
            instr = qiskit_control_flow_mapping[name]
            instr.has_single_gate_props = False
            return instr

        return super().to_non_gate_instruction(name, is_simulator)

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        return {None: None} if is_simulator else {(int(qubit.id),): None for qubit in qubits}

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        return {None: None} if is_simulator else {(int(qubit), int(connected_qubit)): None
                                                  for qubit, connections in connectivity.graph.items()
                                                  for connected_qubit in connections}
