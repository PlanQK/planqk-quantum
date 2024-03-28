from typing import Optional, List

import planqk.qiskit.providers.adapter as adapter
from planqk.qiskit.client.backend_dtos import QubitDto, ConnectivityDto
from planqk.qiskit.providers.qryd.pcp_gate import PCPGate
from planqk.qiskit.providers.qryd.pcz_gate import PCZGate
from qiskit.circuit import Parameter, Gate
from qiskit.circuit.library import PhaseGate, RGate, RXGate, RYGate, HGate, RZGate, UGate, XGate, YGate, ZGate, SXGate, \
    SXdgGate, CXGate, CYGate, CZGate, CPhaseGate, SwapGate, iSwapGate

qryd_gate_name_mapping = {
    "p": PhaseGate(Parameter("lambda")),
    "r": RGate(Parameter("theta"), Parameter("phi")),
    "rx": RXGate(Parameter("theta")),
    "ry": RYGate(Parameter("theta")),
    "pcz": PCZGate(),
    "pcp": PCPGate(Parameter("lambda")),
    "h": HGate(),
    "rz": RZGate(Parameter("theta")),
    "u": UGate(Parameter("theta"), Parameter("phi"), Parameter("lambda")),
    "x": XGate(),
    "y": YGate(),
    "z": ZGate(),
    "sx": SXGate(),
    "sxdg": SXdgGate(),
    "cx": CXGate(),
    "cy": CYGate(),
    "cz": CZGate(),
    "cp": CPhaseGate(Parameter("theta")),
    "swap": SwapGate(),
    "iswap": iSwapGate()
}


class QrydAdapter(adapter.ProviderAdapter):
    def to_gate(self, name: str, is_simulator: bool = False) -> Optional[Gate]:
        name = name.lower()
        return qryd_gate_name_mapping.get(name, None) or Gate(name, 0, [])

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        return {(int(qubit.id),): None for qubit in qubits}

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        # QRyd backend emulators are fully connected
        return {(int(qubit1.id), int(qubit2.id)): None for qubit1 in qubits for qubit2 in qubits
                if qubit1.id != qubit2.id}
