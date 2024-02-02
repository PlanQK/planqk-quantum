from abc import ABC

from qiskit.providers import BackendV2

from planqk.qiskit.options import OptionsV2


class MockBackend(BackendV2, ABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def target(self):
        return None

    @property
    def max_circuits(self):
        return None

    @classmethod
    def _default_options(cls):
        return OptionsV2(foo="bar")

    def run(self, run_input, **options):
        pass
