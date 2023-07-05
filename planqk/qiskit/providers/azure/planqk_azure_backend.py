import logging

from azure.quantum.qiskit.backends.backend import AzureBackend
from qiskit.providers import Backend
from qiskit.qobj import Qobj, QasmQobj

from planqk.qiskit.job import PlanqkJob
from planqk.qiskit.providers.azure.planqk_azure_job import _PlanqkAzureJob

logger = logging.getLogger(__name__)


class _PlanqkAzureBackend(Backend):
    backend_name = None

    def __init__(self, azure_backend: AzureBackend):
        self.backend = azure_backend

    def run(self, circuit, **kwargs):
        """
        Submits the given input to run on an Azure Quantum backend.
        """

        # Some Qiskit features require passing lists of circuits, so unpack those here.
        # We currently only support single-experiment jobs.
        if isinstance(circuit, (list, tuple)):
            if len(circuit) > 1:
                raise NotImplementedError("Multi-experiment jobs are not supported!")
            circuit = circuit[0]

        # If the input was created using qiskit.assemble,
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
        # are calculated from the input itself:
        job_name = kwargs.pop("job_name", circuit.name)
        input_data = self.backend._translate_circuit(circuit, **kwargs)
        metadata = kwargs.pop("metadata") if "metadata" in kwargs else self.backend._job_metadata(circuit, **kwargs)

        # Backend kwargs are mapped to input_params.
        # Take also into consideration kwargs passed in the kwargs, as the take precedence
        # over default values:
        input_params = vars(self.backend.options)
        for opt in kwargs.copy():
            if opt in input_params:
                input_params[opt] = kwargs.pop(opt)

        logger.info(f"Submitting new job for backend {self.name()}")
        job = _PlanqkAzureJob(
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

        logger.info(f"Submitted job with id '{job.id()}' for input '{circuit.name}':")
        logger.info(input_data)

        return job

    def retrieve_job(self, job_id) -> _PlanqkAzureJob:
        """
        Returns the Job instance associated with the given id.
        """
        planqk_job = PlanqkJob(job_id=job_id)
        return _PlanqkAzureJob(backend=self, planqk_job=planqk_job)

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
        Return the kwargs for the backend.

        The kwargs of a backend are the dynamic parameters defining
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
        Return the backend SupportedProviders.

        Returns:
            SupportedProviders: the SupportedProviders responsible for the backend.
        """
        return self.backend.provider()

    def set_options(self, **fields):
        """
        Set the kwargs fields for the backend.

        This method is used to update the kwargs of a backend. If
        you need to change any of the kwargs prior to running just
        pass in the kwarg with the new value for the kwargs.

        Args:
            fields: The fields to update the kwargs

        Raises:
            AttributeError: If the field passed in is not part of the
                kwargs
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
