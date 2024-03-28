from typing import Optional, List

from qiskit.circuit import Gate
from qiskit_braket_provider.providers.adapter import _GATE_NAME_TO_QISKIT_GATE

import planqk.qiskit.providers.adapter as adapter
from planqk.qiskit.client.backend_dtos import QubitDto, ConnectivityDto


class AwsAdapter(adapter.ProviderAdapter):
    """Adapter for AWS Braket backend."""

    def to_gate(self, name: str, is_simulator: bool = False) -> Optional[Gate]:
        name = name.lower()
        gate = _GATE_NAME_TO_QISKIT_GATE.get(name, None)
        # Braket quantum backends only support 1 and 2 qubit gates
        return gate if (gate and gate.num_qubits < 3) or is_simulator else None

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        if is_simulator:
            return {None: None}
        return {(int(qubit.id),): None for qubit in qubits}

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        if is_simulator:
            return {None: None}
        if connectivity.fully_connected:
            return {(int(qubit1.id), int(qubit2.id)): None for qubit1 in qubits for qubit2 in qubits
                    if qubit1.id != qubit2.id}
        else:
            return {(int(qubit), int(connected_qubit)): None
                    for qubit, connections in connectivity.graph.items()
                    for connected_qubit in connections}
