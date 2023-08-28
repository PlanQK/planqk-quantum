from typing import Optional, List

from qiskit.circuit import Instruction as QiskitInstruction, Gate

import planqk.qiskit.providers.adapter as adapter
from planqk.qiskit.client.backend_dtos import QubitDto, ConnectivityDto
from planqk.qiskit.providers.aws_converters import qiskit_gate_name_to_braket_gate_mapping


class AwsAdapter(adapter.ProviderAdapter):
    """Adapter for AWS Braket backend."""

    def op_to_instruction(self, operation: str) -> Optional[QiskitInstruction]:
        operation = operation.lower()
        gate = qiskit_gate_name_to_braket_gate_mapping.get(operation, None) or Gate(operation, 0, [])
        # Braket only supports 1 and 2 qubit gates
        return gate if gate.num_qubits < 3 else None

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        return {(int(qubit.id),): None for qubit in qubits}

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        if connectivity.fully_connected:
            return {(int(qubit1.id), int(qubit2.id)): None for qubit1 in qubits for qubit2 in qubits
                    if qubit1.id != qubit2.id}
        else:
            return {(int(qubit), int(connected_qubit)): None
                    for qubit, connections in connectivity.graph.items()
                    for connected_qubit in connections}
