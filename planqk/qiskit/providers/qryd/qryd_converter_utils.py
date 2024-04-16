from math import pi
from typing import Any
from typing import Dict

from qiskit import QuantumCircuit
from qiskit.providers import Options

from planqk.qiskit.providers.qryd.pcp_gate import PCPGate
from planqk.qiskit.providers.qryd.pcz_gate import PCZGate


def convert_to_wire_format(circuit: QuantumCircuit, options: Options) -> dict:
    """Convert a circuit to a dictionary.

    The method converts a circuit to a Json-serializable dictionary for submitting
    it to the API of QRydDemo's emulator.

    Args:
        circuit: The QuantumCircuit to be converted.
        options: The Options object of the backend.

    Raises:
        RuntimeError: If the `circuit` contains a quantum gate or operation that
            is not supported.
        AssertionError: If the `circuit` contains definitions that are inconsistent
            with definitions used by the web API.

    Returns:
        Json-serializable dictionary describing the simulation job.

    """
    circuit_dict = {
        "ClassicalRegister": {
            "measurement": {
                "circuits": [
                    {
                        "definitions": [
                            {
                                "DefinitionBit": {
                                    "name": "ro",
                                    "length": len(circuit.clbits),
                                    "is_output": True,
                                }
                            }
                        ],
                        "operations": [],
                        "_roqoqo_version": {
                            "major_version": 1,
                            "minor_version": 0,
                        },
                    }
                ],
            },
        },
    }  # type: Dict[str, Any]
    qubits_map = {bit: n for n, bit in enumerate(circuit.qubits)}
    clbits_map = {bit: n for n, bit in enumerate(circuit.clbits)}
    for instruction in circuit.data:
        inst = instruction[0]
        params = inst.params
        qubits = [qubits_map[bit] for bit in instruction[1]]
        clbits = [clbits_map[bit] for bit in instruction[2]]

        if inst.label:
            print(inst.label)  # TODO

        if inst.name == "barrier":
            continue
        elif inst.name == "measure":
            if len(qubits) != len(clbits):
                raise AssertionError(
                    "Number of qubits and classical bits must be same."
                )
            for qubit, clbit in zip(qubits, clbits):
                circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                    "operations"
                ] += [
                    {
                        "MeasureQubit": {
                            "readout": "ro",
                            "qubit": qubit,
                            "readout_index": clbit,
                        }
                    }
                ]
        elif inst.name == "p":
            if len(qubits) != 1 or len(params) != 1:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "PhaseShiftState1": {
                        "qubit": qubits[0],
                        "theta": float(params[0]),
                    }
                }
            ]
        elif inst.name == "r":
            if len(qubits) != 1 or len(params) != 2:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "RotateXY": {
                        "qubit": qubits[0],
                        "theta": float(params[0]),
                        "phi": float(params[1]),
                    }
                }
            ]
        elif inst.name == "rx":
            if len(qubits) != 1 or len(params) != 1:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "RotateX": {
                        "qubit": qubits[0],
                        "theta": float(params[0]),
                    }
                }
            ]
        elif inst.name == "ry":
            if len(qubits) != 1 or len(params) != 1:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "RotateY": {
                        "qubit": qubits[0],
                        "theta": float(params[0]),
                    }
                }
            ]
        elif inst.name == "pcz":
            if len(qubits) != 2 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "PhaseShiftedControlledZ": {
                        "control": qubits[0],
                        "target": qubits[1],
                        "phi": float(PCZGate.get_theta()),
                    }
                }
            ]
        elif inst.name == "pcp":
            if len(qubits) != 2 or len(params) != 1:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "PhaseShiftedControlledPhase": {
                        "control": qubits[0],
                        "target": qubits[1],
                        "theta": float(params[0]),
                        "phi": float(PCPGate.get_theta(float(params[0]))),
                    }
                }
            ]
        elif inst.name == "h":
            if len(qubits) != 1 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "Hadamard": {
                        "qubit": qubits[0],
                    }
                }
            ]
        elif inst.name == "rz":
            if len(qubits) != 1 or len(params) != 1:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "RotateZ": {
                        "qubit": qubits[0],
                        "theta": float(params[0]),
                    }
                }
            ]
        elif inst.name == "u":
            if len(qubits) != 1 or len(params) != 3:
                raise AssertionError("Wrong number of arguments.")
            theta = float(params[0])
            phi = float(params[1])
            lam = float(params[2])
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "RotateZ": {
                        "qubit": qubits[0],
                        "theta": lam - pi / 2,
                    }
                },
                {
                    "RotateX": {
                        "qubit": qubits[0],
                        "theta": theta,
                    }
                },
                {
                    "RotateZ": {
                        "qubit": qubits[0],
                        "theta": phi + pi / 2,
                    }
                },
            ]
        elif inst.name == "x":
            if len(qubits) != 1 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "PauliX": {
                        "qubit": qubits[0],
                    }
                }
            ]
        elif inst.name == "y":
            if len(qubits) != 1 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "PauliY": {
                        "qubit": qubits[0],
                    }
                }
            ]
        elif inst.name == "z":
            if len(qubits) != 1 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "PauliZ": {
                        "qubit": qubits[0],
                    }
                }
            ]
        elif inst.name == "sx":
            if len(qubits) != 1 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "SqrtPauliX": {
                        "qubit": qubits[0],
                    }
                }
            ]
        elif inst.name == "sxdg":
            if len(qubits) != 1 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "InvSqrtPauliX": {
                        "qubit": qubits[0],
                    }
                }
            ]
        elif inst.name == "cx":
            if len(qubits) != 2 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "CNOT": {
                        "control": qubits[0],
                        "target": qubits[1],
                    }
                }
            ]
        elif inst.name == "cy":
            if len(qubits) != 2 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "ControlledPauliY": {
                        "control": qubits[0],
                        "target": qubits[1],
                    }
                }
            ]
        elif inst.name == "cz":
            if len(qubits) != 2 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "ControlledPauliZ": {
                        "control": qubits[0],
                        "target": qubits[1],
                    }
                }
            ]
        elif inst.name == "cp":
            if len(qubits) != 2 or len(params) != 1:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "ControlledPhaseShift": {
                        "control": qubits[0],
                        "target": qubits[1],
                        "theta": float(params[0]),
                    }
                }
            ]
        elif inst.name == "swap":
            if len(qubits) != 2 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "SWAP": {
                        "control": qubits[0],
                        "target": qubits[1],
                    }
                }
            ]
        elif inst.name == "iswap":
            if len(qubits) != 2 or len(params) != 0:
                raise AssertionError("Wrong number of arguments.")
            circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
                "operations"
            ] += [
                {
                    "ISwap": {
                        "control": qubits[0],
                        "target": qubits[1],
                    }
                }
            ]
        else:
            raise RuntimeError("Operation '%s' not supported." % inst.name)

    circuit_dict["ClassicalRegister"]["measurement"]["circuits"][0][
        "operations"
    ] += [
        {
            "PragmaSetNumberOfMeasurements": {
                "readout": "ro",
                "number_measurements": options.shots,
            }
        }
    ]

    return circuit_dict
