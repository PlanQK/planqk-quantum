import json
from typing import Optional, Tuple

from qiskit.circuit import Gate
from qiskit.circuit import IfElseOp, WhileLoopOp, ForLoopOp, SwitchCaseOp, Instruction
from qiskit.circuit import Parameter, Reset
from qiskit.circuit.library import IGate, SXGate, XGate, CXGate, RZGate, ECRGate, CZGate
from qiskit.qobj.utils import MeasLevel, MeasReturnType
from qiskit_ibm_runtime import RuntimeEncoder

from planqk.qiskit import PlanqkBackend
from planqk.qiskit.client.job_dtos import INPUT_FORMAT
from planqk.qiskit.options import OptionsV2

ibm_name_mapping = {
    "id": IGate(),
    "sx": SXGate(),
    "x": XGate(),
    "cx": CXGate(),
    "rz": RZGate(Parameter("λ")),
    "reset": Reset(),
    "ecr": ECRGate(),
    "cz": CZGate(),
}

qiskit_control_flow_mapping = {
    "if_else": IfElseOp,
    "while_loop": WhileLoopOp,
    "for_loop": ForLoopOp,
    "switch_case": SwitchCaseOp,
}


class PlanqkIbmBackend(PlanqkBackend):

    def __init__(self, **kwargs):
        PlanqkBackend.__init__(self, **kwargs)

    def _default_options(self):
        return OptionsV2(
            shots=4000,
            memory=False,
            meas_level=MeasLevel.CLASSIFIED,
            meas_return=MeasReturnType.AVERAGE,
            memory_slots=None,
            memory_slot_size=100,
            rep_time=None,
            rep_delay=None,
            init_qubits=True,
            use_measure_esp=None,
            # Simulator only
            noise_model=None,
            seed_simulator=None,
        )

    def to_gate(self, name: str) -> Optional[Gate]:
        name = name.lower()
        return ibm_name_mapping.get(name, None) or Gate(name, 0, [])

    def get_single_qubit_gate_properties(self) -> dict:
        qubits = self.backend_info.configuration.qubits
        return {None: None} if self.is_simulator else {(int(qubit.id),): None for qubit in qubits}

    def get_multi_qubit_gate_properties(self) -> dict:
        connectivity = self.backend_info.configuration.connectivity
        return {None: None} if self.is_simulator else {(int(qubit), int(connected_qubit)): None
                                                       for qubit, connections in connectivity.graph.items()
                                                       for connected_qubit in connections}

    def to_non_gate_instruction(self, name: str) -> Optional[Instruction]:
        if name in qiskit_control_flow_mapping:
            instr = qiskit_control_flow_mapping[name]
            instr.has_single_gate_props = False
            return instr

        return super().to_non_gate_instruction(name)

    def convert_to_job_input(self, circuit, options=None) -> Tuple[INPUT_FORMAT, dict]:
        # Transforms circuit to base64 encoded byte stream
        input_json_str = json.dumps(circuit, cls=RuntimeEncoder)
        # Transform back to json but with the circuit property base64 encoded
        return json.loads(input_json_str)

    def get_job_input_format(self) -> INPUT_FORMAT:
        return INPUT_FORMAT.QISKIT
