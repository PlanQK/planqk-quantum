from typing import Union

import pytest
from qiskit.providers import Backend, BackendV2
from qiskit.result.models import ExperimentResultData

from planqk.qiskit.client.backend_dtos import PROVIDER
from tests.acceptance.backends.azure_test_utils import init_azure_provider, AZURE_NAME_IONQ_SIM
from tests.acceptance.backends.backends_list import BACKEND_ID_AZURE_IONQ_SIM
from tests.acceptance.backends.base_test import BaseTest
from tests.utils import is_valid_uuid
from tests.utils import transform_decimal_to_bitsrings


@pytest.mark.azure
class AzureIonqSimTests(BaseTest):

    def setUp(self):
        super().setUp()

        self.azure_provider = init_azure_provider()

    def get_provider(self):
        return self.azure_provider

    def get_provider_id(self):
        return PROVIDER.AZURE.name

    def get_backend_id(self) -> str:
        return BACKEND_ID_AZURE_IONQ_SIM

    def get_provider_backend_name(self) -> str:
        return AZURE_NAME_IONQ_SIM

    def get_test_shots(self) -> int:
        return 1

    def is_simulator(self) -> bool:
        return True

    def supports_memory_result(self) -> bool:
        return True

    def get_provider_job_id(self, job_id: str) -> str:
        return job_id

    def is_valid_job_id(self, job_id: str) -> bool:
        return is_valid_uuid(job_id)

    def assert_backend(self, expected: Union[Backend, BackendV2], actual: BackendV2):
        exp_config = expected._configuration
        self.assertEqual(exp_config.backend_name, self.get_provider_backend_name())

        actual_inst_names = sorted([inst[0].name for inst in actual.instructions], key=str)
        self.assertEqual(exp_config.basis_gates, actual_inst_names)
        self.assertEqual(exp_config.backend_name, self.get_provider_backend_name())
        self.assertEqual(exp_config.coupling_map, actual.coupling_map)
        self.assertEqual(exp_config.num_qubits, actual.num_qubits)

        self.assertTrue(actual.description.startswith("PlanQK Backend:"))
        self.assertTrue(actual.description.endswith(actual.name + "."))
        self.assertIsNone(actual.dt)

        # Instructions are not returned by Azure Provider

        self.assertEqual(exp_config.basis_gates, actual_inst_names)
        # Ensure that instructions have no coupling infos
        self.assertTrue(len([inst[1] for inst in actual.instructions if inst[1] is not None]) == 0)

        # check that the values of the instructions were not set
        for inst in actual.instructions:
            self.assertIsNone(inst[0].condition, "Condition attribute is not None")
            self.assertEqual(inst[0].condition_bits, [], "Condition bits are not an empty list")
            self.assertEqual(inst[0].decompositions, [], "Decompositions are not an empty list")
            self.assertIsNone(inst[0].definition, "Definition attribute is not None")
            self.assertIsNone(inst[0].duration, "Duration attribute is not None")
            self.assertIsNone(inst[0].label, "Label attribute is not None")
            if inst[0].name != 'measure':  # Measure is create by SDK and has no qubits
                self.assertEqual(inst[0].num_clbits, 0, "Number of classical bits is not 0")
                self.assertEqual(inst[0].num_qubits, 0, "Number of qubits is not 0")
            self.assertEqual(inst[0].params, [], "Params are not an empty list")
            self.assertEqual(inst[0].unit, 'dt', "Unit attribute is not 'dt'")

        # Operations are not returned by Azure Provider

        self.assert_backend_config(expected, actual.configuration())
        self.assertTrue(len(actual.operation_names) > 0)
        self.assertTrue(len(actual.operations) > 0)
        self.assertIsNotNone(actual.target)
        self.assertEqual(2, actual.version)

    def assert_experimental_result_data(self, exp_result: ExperimentResultData, result: ExperimentResultData):
        num_qubits = len(self.get_input_circuit().qubits)
        exp_counts = transform_decimal_to_bitsrings(exp_result.counts, num_qubits)
        # Ionq simulator returns probabilities, hence, Azure SDK generates random memory values -> memory not asserted
        self.assertTrue(exp_counts == {'111': 1} or exp_counts == {'000': 1})
        self.assertTrue(result.counts == {'111': 1} or result.counts == {'000': 1})
        # But it is checked if a memory is returned as PlanQK generates random memory values for simulators
        self.assertTrue(len(result.memory) == 1)

    # Tests

    def test_should_get_backend(self):
        self.should_get_backend()

    def test_should_transpile_circuit(self):
        # For simulators transpilation is not required
        pass

    def test_should_run_job(self):
        self.should_run_job()

    def test_should_retrieve_job(self):
        self.should_retrieve_job()

    def test_should_retrieve_job_result(self):
        self.should_retrieve_job_result()

    def test_should_cancel_job(self):
        # Skip this test as Azure Ionq simulator does not support cancelling jobs
        pass

    def test_should_retrieve_job_status(self):
        self.should_retrieve_job_status()
