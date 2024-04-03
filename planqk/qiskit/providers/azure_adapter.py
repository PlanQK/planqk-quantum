from typing import Optional, List

from planqk.qiskit.client.backend_dtos import QubitDto, ConnectivityDto
from planqk.qiskit.providers.adapter import ProviderAdapter
from qiskit.circuit import Gate


class AzureAdapter(ProviderAdapter):
    def to_gate(self, name: str, is_simulator: bool = False) -> Optional[Gate]:
        name = name.lower()
        return Gate(name, 0, [])

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        return {None: None}

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        return {None: None}
