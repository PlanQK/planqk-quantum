import logging
import time
import unittest
from uuid import UUID

import pytest
import qiskit
from azure.identity import ClientSecretCredential
from azure.quantum import Workspace
from azure.quantum.qiskit import AzureQuantumProvider
from azure.quantum.qiskit.backends import QuantinuumQPUBackend
from qiskit.providers import JobStatus, Backend
from qiskit import Aer, QuantumCircuit, transpile
from qiskit.result import Counts
import os

from planqk.qiskit import PlanqkQuantumProvider, PlanqkQuantumJob

logging.basicConfig(level=logging.DEBUG)

# overwrite base url
os.environ['PLANQK_QUANTUM_BASE_URL'] = 'http://127.0.0.1:8080'
# set access token
#os.environ['PLANQK_QUANTUM_ACCESS_TOKEN'] = None


def is_valid_uuid(uuid_to_test):
    try:
        uuid_obj = UUID(str(uuid_to_test))
    except ValueError:
        return False
    return True


class BasicTestSuite(unittest.TestCase):
    #TODO get backends from azure povider

    def setUp(self):
        credential = ClientSecretCredential(tenant_id="3871fdd8-273b-4217-bba4-03ddd57c8785",
                                            client_id="48db1ba7-ec70-45a0-9d21-b4f4f48d129f",
                                            client_secret="THy8Q~J1u3.3UW6gqxkvVGZse6efDLslhbW.zbho")
        workspace = Workspace(
            # Format must match
            resource_id="/subscriptions/57e31d8b-7609-4a9a-a8bd-c1b9a7b6042b/resourceGroups/PlanQK/providers/Microsoft.Quantum/Workspaces/planqk-workspace",
            location='West Europe',
            credential=credential
        )
        provider = AzureQuantumProvider(
            workspace=workspace
        )
        self.azure_provider = provider
        self.planqk_provider = PlanqkQuantumProvider("123")

    def test_should_list_all_backends(self):
        # Get backend names via AzureProvider
        exp_backend_names = []
        for backend in self.azure_provider.backends():
            exp_backend_names.append(backend.name())

        # Get backend names via PlanqkProvider
        backend_names = []
        for backend in self.planqk_provider.backends():
            backend_names.append(backend.name())

        assert set(backend_names) == set(exp_backend_names)

    def test_should_get_backend(self):
        # Get backend via AzureProvider
        exp_backend = self.azure_provider.get_backend("quantinuum.hqs-lt-s1")

        # Get backend via PlanqkProvider
        backend = self.planqk_provider.get_backend("quantinuum.hqs-lt-s1")

        assert backend.name() == exp_backend.name()
        assert backend.backend_name == exp_backend.backend_name
        assert set(backend.backend_names) == set(exp_backend.backend_names)
        assert backend.configuration() == exp_backend.configuration()
        assert backend.options.count == exp_backend.options.count
        assert backend.status() == exp_backend.status()
        assert backend.version == exp_backend.version

    # @pytest.mark.skip(reason="enable for local integration testing")
    def test_should_run_local_job(self):

        sim_backend = self.planqk_provider.get_backend("ionq.simulator")
        circuit = self.get_sample_circuit(sim_backend)
        job = sim_backend.run(circuit, shots=1)
        #job = qiskit.execute(circuit, backend=backend, shots=1) EXECUTE?
        job_id = job.id()

        assert is_valid_uuid(job_id)

    def test_should_retrieve_job(self):
        # Given: create job
        azure_backend = self.azure_provider.get_backend("ionq.simulator")
        circuit = self.get_sample_circuit(azure_backend)
        job = azure_backend.run(circuit, shots=1)

        # When

        # Get job via Azure
        exp_job = azure_backend.retrieve_job(job.id())

        # Get job via PlanQK
        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(job.id())

        # Then
        assert exp_job.id() == job.id()
        assert exp_job.version == job.version

    def test_should_retrieve_job_status(self):
        azure_backend = self.azure_provider.get_backend("ionq.simulator")
        circuit = self.get_sample_circuit(azure_backend)
        job = azure_backend.run(circuit, shots=1)

        # Get job status via PlanQK
        job = self.planqk_provider.get_backend("ionq.simulator").retrieve_job(job.id())
        job_status = job.status()

        # Then
        self.assertIn(job_status.name, [JobStatus.QUEUED.name, JobStatus.DONE.name])

    def test_should_cancel_job(self):
        azure_backend = self.azure_provider.get_backend("ionq.simulator")
        circuit = self.get_sample_circuit(azure_backend)
        job = azure_backend.run(circuit, shots=1)

        job.cancel()



    def test_should_execute_job_on_all_backends(self):
        pass

    def get_sample_circuit(self, backend: Backend):
        circuit = QuantumCircuit(3, 3)
        circuit.name = "Qiskit Sample - 3-qubit GHZ circuit"
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure([0, 1, 2], [0, 1, 2])

        circuit = transpile(circuit, backend)

        return circuit

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
