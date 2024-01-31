import unittest

from qiskit_aer import AerSimulator

from planqk.qiskit import PlanqkJob
from planqk.qiskit.client.job_dtos import JobDto


class JobTestSuite(unittest.TestCase):

    def test_job_should_have_queue_position_attribute(self):
        backend = AerSimulator()
        job = PlanqkJob(backend, job_id="1337", job_details=JobDto(**{"provider": "TEST"}))

        queue_position = job.queue_position()

        self.assertIsNone(queue_position)
