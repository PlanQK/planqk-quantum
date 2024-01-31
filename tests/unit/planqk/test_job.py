import unittest
from abc import ABC

from qiskit.providers import BackendV2

from planqk.qiskit import PlanqkJob
from planqk.qiskit.client.job_dtos import JobDto


class TestBackend(BackendV2, ABC):

    @property
    def target(self):
        return None

    @property
    def max_circuits(self):
        return None

    @classmethod
    def _default_options(cls):
        pass

    def run(self, run_input, **options):
        pass


class JobTestSuite(unittest.TestCase):

    def test_job_should_have_queue_position_attribute(self):
        backend = TestBackend()
        job = PlanqkJob(backend, job_id="1337", job_details=JobDto(**{"provider": "TEST"}))

        queue_position = job.queue_position()

        self.assertIsNone(queue_position)
