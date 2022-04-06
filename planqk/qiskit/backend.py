import base64
import logging
from math import log2

import qiskit
from qiskit import Aer
from qiskit.providers import BackendV1, ProviderV1, Options, QiskitBackendNotFoundError
from qiskit.providers.models import BackendConfiguration
from qiskit.utils import local_hardware_info

from planqk.client import PlanqkClient
from planqk.qiskit.job import PlanqkQuantumJob

logger = logging.getLogger(__name__)

SYSTEM_MEMORY_GB = local_hardware_info()['memory']
MAX_QUBITS = int(log2(SYSTEM_MEMORY_GB * (1024 ** 3) / 16))

_DEFAULT_BASIS_GATES = sorted([
    'u1', 'u2', 'u3', 'u', 'p', 'r', 'rx', 'ry', 'rz', 'id', 'x',
    'y', 'z', 'h', 's', 'sdg', 'sx', 'sxdg', 't', 'tdg', 'swap', 'cx',
    'cy', 'cz', 'csx', 'cp', 'cu', 'cu1', 'cu2', 'cu3', 'rxx', 'ryy',
    'rzz', 'rzx', 'ccx', 'cswap', 'mcx', 'mcy', 'mcz', 'mcsx',
    'mcp', 'mcphase', 'mcu', 'mcu1', 'mcu2', 'mcu3', 'mcrx', 'mcry', 'mcrz',
    'mcr', 'mcswap', 'unitary', 'diagonal', 'multiplexer',
    'initialize', 'delay', 'pauli', 'mcx_gray'
])

_DEFAULT_CONFIGURATION = {
    'n_qubits': MAX_QUBITS,
    'simulator': True,
    'local': True,
    'conditional': True,
    'open_pulse': False,
    'memory': True,
    'max_shots': int(1e6),
    'coupling_map': None,
    'basis_gates': _DEFAULT_BASIS_GATES,
    'custom_instructions': [],
    'gates': []
}


class PlanqkQuantumBackend(BackendV1):
    def __init__(self, client: PlanqkClient, backend_name: str, provider: ProviderV1, **kwargs):
        self._client = client
        self.backend_name = backend_name
        configuration = BackendConfiguration.from_dict({
            **_DEFAULT_CONFIGURATION,
            **{
                'backend_name': backend_name,
                'backend_version': self.version,
            }})
        super().__init__(configuration=configuration, provider=provider, **kwargs)

    def _default_options(self):
        return Options(shots=1)

    def run(self, circuit, **kwargs):
        logger.info(f'Submitting new job for backend {self.name()}')

        try:
            backend = Aer.get_backend(name=self.backend_name)
            logger.debug('Aer backend detected; execute locally...')
            job = qiskit.execute(circuit, backend=backend, **kwargs)
            return job
        except QiskitBackendNotFoundError:
            logger.debug('IMBQ backend detected; execute remotely...')

        circuit_qasm = circuit.qasm()
        circuit_qasm_bytes = circuit_qasm.encode('utf-8')
        circuit_qasm_base64 = base64.b64encode(circuit_qasm_bytes)
        circuit_qasm_base64_string = str(circuit_qasm_base64, 'utf-8')
        job = PlanqkQuantumJob(
            client=self._client,
            backend=self,
            circuit_qasm=circuit_qasm_base64_string,
            qubits=circuit.num_qubits,
            **kwargs
        )
        logger.info(f'Submitted job with id "{job.job_id()}" for circuit "{circuit.name}":')
        return job
