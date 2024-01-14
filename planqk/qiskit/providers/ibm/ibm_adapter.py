from typing import Optional, List

from qiskit.circuit import Instruction as QiskitInstruction, Gate
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


class IbmAdapter(ProviderAdapter):
    def op_to_instruction(self, operation: str) -> Optional[QiskitInstruction]:
        operation = operation.lower()
        return ibm_name_mapping.get(operation, None) or Gate(operation, 0, [])

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        return {None: None} if is_simulator else {(int(qubit.id),): None for qubit in qubits}

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        return {None: None} if is_simulator else {(int(qubit), int(connected_qubit)): None
                                                  for qubit, connections in connectivity.graph.items()
                                                  for connected_qubit in connections}
