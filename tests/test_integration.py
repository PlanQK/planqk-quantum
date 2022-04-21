import logging
import os
import unittest

import pytest
import qiskit
from qiskit.providers import JobStatus
from qiskit.providers.aer import AerJob
from qiskit.result import Counts

from planqk.qiskit import PlanqkQuantumProvider, PlanqkQuantumJob

logging.basicConfig(level=logging.DEBUG)

# overwrite base url
os.environ['PLANQK_QUANTUM_BASE_URL'] = 'http://127.0.0.1:8000'
# set access token
os.environ['PLANQK_QUANTUM_ACCESS_TOKEN'] \
    = '7439cead03a3429bd4f49dbf832fa181b0ffc01cb4435a19e6ae736aa1126055aa64da0faada22c8'


class BasicTestSuite(unittest.TestCase):

    @pytest.mark.skip(reason="enable for local integration testing")
    def test_should_execute_local_job(self):
        n_bits = 5
        circuit = qiskit.QuantumCircuit(n_bits)
        circuit.h(range(n_bits))
        circuit.measure_all()
        provider = PlanqkQuantumProvider()
        backend = provider.get_backend(name='aer_simulator')
        job = qiskit.execute(circuit, backend=backend, shots=1)
        assert type(job) is AerJob

    @pytest.mark.skip(reason="enable for local integration testing")
    def test_should_execute_remote_job(self):
        n_bits = 5
        circuit = qiskit.QuantumCircuit(n_bits)
        circuit.h(range(n_bits))
        circuit.measure_all()
        provider = PlanqkQuantumProvider()
        backend = provider.get_backend(name='ibmq_qasm_simulator')
        job = qiskit.execute(circuit, backend=backend, shots=1)
        assert type(job) is PlanqkQuantumJob
        assert type(job.status()) is JobStatus
        result_counts = job.result().get_counts()
        assert type(result_counts) is Counts


if __name__ == '__main__':
    unittest.main()
