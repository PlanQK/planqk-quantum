from azure.quantum.qiskit.backends.backend import AzureBackend
from qiskit.providers import Backend
from qiskit.qobj import Qobj, QasmQobj

import logging

from planqk.client import PlanqkClient
from planqk.qiskit.planqk_job import PlanqkJob
from planqk.qiskit.providers.azure.planqk_azure_job import PlanqkAzureJob

logger = logging.getLogger(__name__)


class PlanqkAzureBackend(Backend):
    backend_name = None

    def __init__(self, client: PlanqkClient, azure_backend: AzureBackend):
        self._client = client
        self.backend = azure_backend

    def run(self, circuit, **kwargs):
        """Submits the given circuit to run on an Azure Quantum backend."""

        # Some Qiskit features require passing lists of circuits, so unpack those here.
        # We currently only support single-experiment jobs.
        if isinstance(circuit, (list, tuple)):
            if len(circuit) > 1:
                raise NotImplementedError("Multi-experiment jobs are not supported!")
            circuit = circuit[0]

        # If the circuit was created using qiskit.assemble,
        # disassemble into QASM here
        if isinstance(circuit, QasmQobj) or isinstance(circuit, Qobj):
            from qiskit.assembler import disassemble
            circuits, run, _ = disassemble(circuit)
            circuit = circuits[0]
            if kwargs.get("shots") is None:
                # Note that the default number of shots for QObj is 1024
                # unless the user specifies the backend.
                kwargs["shots"] = run["shots"]

        # The default of these job parameters come from the AzureBackend configuration:
        config = self.configuration()
        provider_id = kwargs.pop("provider_id", config.azure["provider_id"])
        input_data_format = kwargs.pop("input_data_format", config.azure["input_data_format"])
        output_data_format = kwargs.pop("output_data_format", config.azure["output_data_format"])

        # If not provided as kwargs, the values of these parameters
        # are calculated from the circuit itself:
        job_name = kwargs.pop("job_name", circuit.name)
        input_data = self.backend._translate_circuit(circuit, **kwargs)
        metadata = kwargs.pop("metadata") if "metadata" in kwargs else self.backend._job_metadata(circuit, **kwargs)

        # Backend options are mapped to input_params.
        # Take also into consideration options passed in the kwargs, as the take precedence
        # over default values:
        input_params = vars(self.backend.options)
        for opt in kwargs.copy():
            if opt in input_params:
                input_params[opt] = kwargs.pop(opt)

        logger.info(f"Submitting new job for backend {self.name()}")
        job = PlanqkAzureJob(
            client=self._client,
            backend=self,
            target=self.name(),
            name=job_name,
            provider_id=provider_id,
            input_data=input_data.decode("utf-8"),
            input_data_format=input_data_format,
            output_data_format=output_data_format,
            input_params=input_params,
            metadata=metadata,
            **kwargs
        )

        logger.info(f"Submitted job with id '{job.id()}' for circuit '{circuit.name}':")
        logger.info(input_data)

        return job

    def retrieve_job(self, job_id) -> PlanqkAzureJob:
        """ Returns the Job instance associated with the given id."""
        planqk_job = PlanqkJob(self._client, job_id=job_id)
        return PlanqkAzureJob(client=self._client, backend=self, planqk_job=planqk_job)

    def name(self):
        return self.backend.name()

    @property
    def backend_name(self):
        return self.backend.backend_name

    @property
    def backend_names(self):
        return self.backend.backend_names

    @property
    def configuration(self):
        return self.backend.configuration

    @property
    def options(self):
        return self.backend.options

    @property
    def properties(self):
        return self.backend.properties

    def provider(self):
        return self.backend.provider()

    def set_options(self, **fields):
        self.backend.set_options(**fields)

    def status(self):
        return self.backend.status()

    @property
    def version(self):
        return self.backend.version

