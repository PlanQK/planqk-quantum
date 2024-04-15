from planqk.qiskit.providers.ibm.ibm_backend import PlanqkIbmBackend


class PlanqkIbmRuntimeBackend(PlanqkIbmBackend):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
