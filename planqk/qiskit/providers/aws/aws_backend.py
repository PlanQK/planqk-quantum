from typing import Optional

from qiskit.circuit import Gate
from qiskit_braket_provider.providers.adapter import _GATE_NAME_TO_QISKIT_GATE

from planqk.qiskit import PlanqkBackend
from planqk.qiskit.options import OptionsV2


class PlanqkAwsBackend(PlanqkBackend):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def _default_options(cls):
        return OptionsV2()

    def to_gate(self, name: str) -> Optional[Gate]:
        name = name.lower()
        gate = _GATE_NAME_TO_QISKIT_GATE.get(name, None)
        # Braket quantum backends only support 1 and 2 qubit gates
        return gate if (gate and gate.num_qubits < 3) or self.is_simulator else None

    def get_single_qubit_gate_properties(self) -> dict:
        if self.is_simulator:
            return {None: None}
        return {(int(qubit.id),): None for qubit in self.backend_info.configuration.qubits}

    def get_multi_qubit_gate_properties(self) -> dict:
        qubits = self.backend_info.configuration.qubits
        connectivity = self.backend_info.configuration.connectivity
        if self.is_simulator:
            return {None: None}
        if connectivity.fully_connected:
            return {(int(qubit1.id), int(qubit2.id)): None for qubit1 in qubits for qubit2 in qubits
                    if qubit1.id != qubit2.id}
        else:
            return {(int(qubit), int(connected_qubit)): None
                    for qubit, connections in connectivity.graph.items()
                    for connected_qubit in connections}
