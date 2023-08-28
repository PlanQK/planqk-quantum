from typing import Optional, List

from qiskit.circuit import Instruction as QiskitInstruction, Gate

from planqk.qiskit.client.backend_dtos import QubitDto, ConnectivityDto
from planqk.qiskit.providers.adapter import ProviderAdapter


class AzureAdapter(ProviderAdapter):
    def op_to_instruction(self, operation: str) -> Optional[QiskitInstruction]:
        operation = operation.lower()
        return Gate(operation, 0, [])

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        return {None: None}

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        return {None: None}
