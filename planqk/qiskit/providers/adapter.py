from typing import Optional, List

from planqk.qiskit.client.backend_dtos import PROVIDER, QubitDto, ConnectivityDto
from qiskit.circuit import Instruction as QiskitInstruction


class ProviderAdapter:
    def op_to_instruction(self, operation: str) -> Optional[QiskitInstruction]:
        pass

    def single_qubit_gate_props(self, qubits: List[QubitDto], is_simulator: bool = False):
        pass

    def multi_qubit_gate_props(self, qubits: List[QubitDto], connectivity: ConnectivityDto, is_simulator: bool = False):
        pass


class ProviderAdapterFactory:

    @staticmethod
    def get_adapter(provider: PROVIDER) -> ProviderAdapter:
        from planqk.qiskit.providers.aws_adapter import AwsAdapter
        from planqk.qiskit.providers.azure_adapter import AzureAdapter
        from planqk.qiskit.providers.ibm_adapter import IbmAdapter

        if provider == PROVIDER.AWS:
            return AwsAdapter()
        elif provider == PROVIDER.AZURE:
            return AzureAdapter()
        elif provider in {PROVIDER.IBM, PROVIDER.IBM_CLOUD, PROVIDER.TSYSTEMS}:
            return IbmAdapter()
        else:
            raise ValueError(f"Provider {provider} not supported")
