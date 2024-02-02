import unittest

from planqk.qiskit import PlanqkJob
from planqk.qiskit.client.job_dtos import JobDto
from tests.unit.planqk.backends import MockBackend


class JobTestSuite(unittest.TestCase):

    def test_job_should_have_queue_position_attribute(self):
        backend = MockBackend()
        job = PlanqkJob(backend, job_id="1337", job_details=JobDto(**{"provider": "TEST"}))

        queue_position = job.queue_position()

        self.assertIsNone(queue_position)
