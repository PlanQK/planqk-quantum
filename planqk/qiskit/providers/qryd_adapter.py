from typing import Optional, List

from qiskit.circuit import Instruction as QiskitInstruction

import planqk.qiskit.providers.adapter as adapter
from planqk.qiskit.client.backend_dtos import QubitDto, ConnectivityDto


class QrydAdapter(adapter.ProviderAdapter):
    def op_to_instruction(self, operation: str) -> Optional[QiskitInstruction]:
        pass

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        pass

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        pass
