import logging
import os
import unittest

import qiskit
from qiskit.providers import JobStatus
from qiskit.providers.aer import AerJob
from qiskit.result import Counts

from anaqor.qiskit import AnaqorQuantumProvider, AnaqorQuantumJob

logging.basicConfig(level=logging.DEBUG)

# overwrite base url
os.environ['ANAQOR_QUANTUM_BASE_URL'] = 'http://engine.34.107.19.77.nip.io'
# set access token
os.environ[
    'ANAQOR_QUANTUM_ACCESS_TOKEN'] = 'a8ec83b94e6c26a673bf09b99e5eb983c830f535c4eb154e7f6b940558b5ea2d99bcda66884f3d4d'


class BasicTestSuite(unittest.TestCase):

    def test_should_execute_local_job(self):
        n_bits = 5
        circuit = qiskit.QuantumCircuit(n_bits)
        circuit.h(range(n_bits))
        circuit.measure_all()
        provider = AnaqorQuantumProvider()
        backend = provider.get_backend(name='aer_simulator')
        job = qiskit.execute(circuit, backend=backend, shots=1)
        assert type(job) is AerJob

    def test_should_execute_remote_job(self):
        n_bits = 5
        circuit = qiskit.QuantumCircuit(n_bits)
        circuit.h(range(n_bits))
        circuit.measure_all()
        provider = AnaqorQuantumProvider()
        backend = provider.get_backend(name='ibmq_qasm_simulator')
        job = qiskit.execute(circuit, backend=backend, shots=1)
        assert type(job) is AnaqorQuantumJob
        assert type(job.status()) is JobStatus
        result_counts = job.result().get_counts()
        assert type(result_counts) is Counts


if __name__ == '__main__':
    unittest.main()
