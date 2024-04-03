from planqk.qiskit import PlanqkBackend
from planqk.qiskit.options import OptionsV2
from qiskit.qobj.utils import MeasLevel, MeasReturnType


class PlanqkIbmBackend(PlanqkBackend):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _default_options(self):
        return OptionsV2(
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
