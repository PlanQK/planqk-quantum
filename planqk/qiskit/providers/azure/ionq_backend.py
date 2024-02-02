from planqk.qiskit import PlanqkBackend
from planqk.qiskit.options import OptionsV2


class PlanqkAzureIonqBackend(PlanqkBackend):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def _default_options(cls):
        return OptionsV2(
            gateset="qis",
        )
