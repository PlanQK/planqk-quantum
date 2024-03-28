from typing import Optional, List

from qiskit.circuit import Gate, Delay, Parameter, Measure
from qiskit.circuit import Instruction as QiskitInstruction

from planqk.qiskit.client.backend_dtos import PROVIDER, QubitDto, ConnectivityDto


class ProviderAdapter:
    non_gate_instr_mapping = {
        "delay": Delay(Parameter("t")),
        "measure": Measure(),
    }

    def to_gate(self, name: str, is_simulator: bool = False) -> Optional[Gate]:
        pass

    def to_non_gate_instruction(self, name: str, is_simulator: bool = False) -> Optional[QiskitInstruction]:
        instr = self.non_gate_instr_mapping.get(name, None)
        if instr is not None:
            instr.has_single_gate_props = True
            return instr
        return None

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        pass

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        pass


class ProviderAdapterFactory:

    @staticmethod
    def get_adapter(provider: PROVIDER) -> ProviderAdapter:
        from planqk.qiskit.providers.aws_adapter import AwsAdapter
        from planqk.qiskit.providers.azure_adapter import AzureAdapter
        from planqk.qiskit.providers.ibm.ibm_adapter import IbmAdapter
        from planqk.qiskit.providers.qryd.qryd_adapter import QrydAdapter

        if provider == PROVIDER.AWS:
            return AwsAdapter()
        elif provider == PROVIDER.AZURE:
            return AzureAdapter()
        elif provider in {PROVIDER.IBM, PROVIDER.IBM_CLOUD, PROVIDER.TSYSTEMS}:
            return IbmAdapter()
        elif provider == PROVIDER.QRYD:
            return QrydAdapter()
        else:
            raise ValueError(f"Provider {provider} not supported")
