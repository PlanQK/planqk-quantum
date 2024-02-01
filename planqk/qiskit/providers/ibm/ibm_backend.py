import datetime

from qiskit.providers import Options
from qiskit.qobj.utils import MeasLevel, MeasReturnType

from planqk.qiskit import PlanqkBackend, PlanqkQuantumProvider
from planqk.qiskit.client.backend_dtos import BackendDto


class PlanqkIbmBackend(PlanqkBackend):
    """Backend class interfacing with Qryd."""

    def __init__(self, backend_info: BackendDto,
                 provider: PlanqkQuantumProvider,
                 name: str = None,
                 description: str = None,
                 online_date: datetime.datetime = None,
                 backend_version: str = None,
                 **fields, ):
        """Initialize the IBM backend.

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

        Returns: An Options object.
        """
        return Options(
            shots=4000,
            memory=False,
            meas_level=MeasLevel.CLASSIFIED,
            meas_return=MeasReturnType.AVERAGE,
            memory_slots=None,
            memory_slot_size=100,
            rep_time=None,
            rep_delay=None,
            init_qubits=True,
            use_measure_esp=None,
            # Simulator only
            noise_model=None,
            seed_simulator=None,
        )
