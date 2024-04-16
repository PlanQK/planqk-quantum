from typing import Optional

from qiskit.circuit import Gate
from qiskit_ionq.helpers import qiskit_circ_to_ionq_circ

from planqk.qiskit import PlanqkBackend
from planqk.qiskit.client.job_dtos import INPUT_FORMAT


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

    def convert_to_job_input(self, circuit, options):
        gateset = options.get("gateset", "qis")
        ionq_circ, _, _ = qiskit_circ_to_ionq_circ(circuit, gateset=gateset)
        return {
            "gateset": gateset,
            "qubits": circuit.num_qubits,
            "circuit": ionq_circ,
        }

    def get_job_input_format(self) -> INPUT_FORMAT:
        return INPUT_FORMAT.IONQ_CIRCUIT_V1
