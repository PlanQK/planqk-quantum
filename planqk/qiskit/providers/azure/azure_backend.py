from typing import Optional

from qiskit.circuit import Gate

from planqk.qiskit import PlanqkBackend


class PlanqkAzureBackend(PlanqkBackend):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_gate(self, name: str) -> Optional[Gate]:
        name = name.lower()
        return Gate(name, 0, [])

    def get_single_qubit_gate_properties(self) -> dict:
        return {None: None}

    def get_multi_qubit_gate_properties(self) -> dict:
        return {None: None}
