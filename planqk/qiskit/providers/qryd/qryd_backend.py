import datetime

from qiskit.providers import Options

from planqk.qiskit import PlanqkBackend, PlanqkQuantumProvider
from planqk.qiskit.client.backend_dtos import BackendDto


class PlanqkQrydBackend(PlanqkBackend):
    """Backend class interfacing with Qryd."""

    def __init__(self, backend_info: BackendDto,
                 provider: PlanqkQuantumProvider,
                 name: str = None,
                 description: str = None,
                 online_date: datetime.datetime = None,
                 backend_version: str = None,
                 **fields, ):
        """Initialize the Qryd backend.

        Args:
            backend_info: PlanQK backend info
            provider: Qiskit provider for this backend
            name: name of backend
            description: description of backend
            online_date: online date
            backend_version: backend version
            **fields: other arguments
        """
        super().__init__(
            backend_info=backend_info,
            provider=provider,
            name=backend_info.id,
            description=f"PlanQK Backend: {backend_info.hardware_provider.name} {backend_info.id}.",
            online_date=backend_info.updated_at,
            backend_version="2", )

    def _default_options(cls):
        """Get default options.

        Returns:
            An Options object.

        """
        return Options(
            shots=1024,
            memory=False,
            seed_simulator=None,
            seed_compiler=None,
            allow_compilation=True,
            fusion_max_qubits=4,
            use_extended_set=True,
            use_reverse_traversal=True,
            extended_set_size=5,
            extended_set_weight=0.5,
            reverse_traversal_iterations=3,
        )
