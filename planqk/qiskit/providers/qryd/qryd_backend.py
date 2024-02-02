from planqk.qiskit import PlanqkBackend
from planqk.qiskit.options import OptionsV2


class PlanqkQrydBackend(PlanqkBackend):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _default_options(self):
        return OptionsV2(
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
