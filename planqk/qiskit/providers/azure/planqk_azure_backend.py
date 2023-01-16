import logging

from azure.quantum.qiskit.backends.backend import AzureBackend
from qiskit.providers import Backend
from qiskit.qobj import Qobj, QasmQobj

from planqk.client import PlanqkClient
from planqk.qiskit.job import PlanqkJob
from planqk.qiskit.providers.azure.planqk_azure_job import PlanqkAzureJob

logger = logging.getLogger(__name__)


class PlanqkAzureBackend(Backend):
    backend_name = None

    def __init__(self, client: PlanqkClient, azure_backend: AzureBackend):
        self._client = client
        self.backend = azure_backend

    def run(self, circuit, **kwargs):
        """
        Submits the given circuit to run on an Azure Quantum backend.
        """

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
        """
        Returns the Job instance associated with the given id.
        """
        planqk_job = PlanqkJob(self._client, job_id=job_id)
        return PlanqkAzureJob(client=self._client, backend=self, planqk_job=planqk_job)

    def name(self):
        """
        Return the backend name.

        Returns:
            str: the name of the backend.
        """
        return self.backend.name()

    @property
    def backend_name(self):
        """
        Return the backend name.

        Returns:
            str: the name of the backend.
        """
        return self.backend.backend_name

    @property
    def backend_names(self):
        """
        Return the names for the backend.

        Returns:
            tuple: the name of the backend.
        """
        return self.backend.backend_names

    @property
    def configuration(self):
        """
        Return the backend configuration.

       Returns:
           BackendConfiguration: the configuration for the backend.
       """
        return self.backend.configuration

    @property
    def options(self):
        """
        Return the options for the backend.

        The options of a backend are the dynamic parameters defining
        how the backend is used. These are used to control the :meth:`run` method.
        """
        return self.backend.options

    @property
    def properties(self):
        """
        Return the backend properties.

        Returns:
            BackendProperties: the configuration for the backend. If the backend
            does not support properties, it returns ``None``.
        """
        return self.backend.properties

    def provider(self):
        """
        Return the backend Provider.

        Returns:
            Provider: the Provider responsible for the backend.
        """
        return self.backend.provider()

    def set_options(self, **fields):
        """
        Set the options fields for the backend.

        This method is used to update the options of a backend. If
        you need to change any of the options prior to running just
        pass in the kwarg with the new value for the options.

        Args:
            fields: The fields to update the options

        Raises:
            AttributeError: If the field passed in is not part of the
                options
        """
        self.backend.set_options(**fields)

    def status(self):
        """
        Return the backend status.

        Returns:
            BackendStatus: the status of the backend.
        """
        return self.backend.status()

    @property
    def version(self):
        """
        Return the backend version.

       Returns:
           str: the version number of the backend.
       """
        return self.backend.version
