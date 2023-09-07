from dataclasses import dataclass
from datetime import time, datetime
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional

from planqk.qiskit.client.dto_utils import init_with_defined_params
from planqk.qiskit.client.job_dtos import INPUT_FORMAT


class PROVIDER(Enum):
    AZURE = "AZURE"
    AWS = "AWS"
    DWAVE = "DWAVE"
    IBM = "IBM"
    IBM_CLOUD = "IBM_CLOUD"


class TYPE(Enum):
    QPU = "QPU"
    SIMULATOR = "SIMULATOR"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, type_str):
        try:
            return TYPE(type_str)
        except KeyError:
            return cls.UKNOWN


class HARDWARE_PROVIDER(Enum):
    IONQ = "IonQ"
    RIGETTI = "Rigetti"
    OQC = "Oxford Quantum Computers"
    AWS = "AWS Braket"
    AZURE = "Azure Quantum"
    IBM = "IBM Quantum"
    UKNOWN = "Unknown"

    @classmethod
    def from_str(cls, hw_provider_str):
        try:
            return HARDWARE_PROVIDER(hw_provider_str)
        except KeyError:
            return cls.UKNOWN


class STATUS(Enum):
    """
    STATUS Enum:

    UNKNOWN: The actual status is unknown.
    ONLINE: The actual is online, processing submitted jobs and accepting new ones.
    PAUSED: The actual is accepting jobs, but not currently processing them.
    OFFLINE: The actual is not accepting new jobs, e.g. due to maintenance.
    RETIRED: The actual is not available for use anymore.
    """
    UNKNOWN = "UNKNOWN"
    ONLINE = "ONLINE"
    PAUSED = "PAUSED"
    OFFLINE = "OFFLINE"
    RETIRED = "RETIRED"

    @classmethod
    def from_str(cls, status_str):
        try:
            return STATUS(status_str)
        except KeyError:
            return cls.UKNOWN


@dataclass
class DocumentationDto:
    description: Optional[str] = None
    url: Optional[str] = None
    # status_url: Optional[str] = None
    location: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict):  # TODO das auf alle inits anwenden
        return init_with_defined_params(cls, data)


@dataclass
class QubitDto:
    id: str

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


@dataclass
class GateDto:
    name: str
    native: bool

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


@dataclass
class ConnectivityDto:
    fully_connected: bool
    graph: Optional[Dict[str, List[str]]] = None

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


@dataclass
class ShotsRangeDto:
    min: int
    max: int

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


@dataclass
class ConfigurationDto:
    gates: List[GateDto]
    instructions: List[str]
    qubits: List[QubitDto]
    qubit_count: int
    connectivity: ConnectivityDto
    supported_input_formats: List[INPUT_FORMAT]
    shots_range: ShotsRangeDto
    memory_result_returned: bool

    def __post_init__(self):
        self.gates = [GateDto.from_dict(gate) for gate in self.gates]
        self.qubits = [QubitDto.from_dict(qubit) for qubit in self.qubits]
        self.connectivity = ConnectivityDto.from_dict(self.connectivity)
        self.supported_input_formats = [INPUT_FORMAT(input_format) for input_format in self.supported_input_formats]
        self.shots_range = ShotsRangeDto.from_dict(self.shots_range)

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


@dataclass
class AvailabilityTimesDto:
    granularity: str
    start: time
    end: time

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


@dataclass
class CostDto:
    granularity: str
    currency: str
    value: float

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


@dataclass
class BackendDto:
    id: str
    provider: PROVIDER
    internal_id: Optional[str] = None
    hardware_provider: Optional[HARDWARE_PROVIDER] = None
    name: Optional[str] = None
    documentation: Optional[DocumentationDto] = None
    configuration: Optional[ConfigurationDto] = None
    type: Optional[TYPE] = None
    status: Optional[STATUS] = None
    availability: Optional[List[AvailabilityTimesDto]] = None
    costs: Optional[List[CostDto]] = None
    updated_at: Optional[datetime] = None
    avg_queue_time: Optional[int] = None

    def __post_init__(self):
        self.provider = PROVIDER(self.provider)
        self.hardware_provider = HARDWARE_PROVIDER.from_str(self.hardware_provider) if self.hardware_provider else None
        self.type = TYPE(self.type) if self.type else None
        self.status = STATUS(self.status) if self.status else None
        self.documentation = DocumentationDto.from_dict(self.documentation) if self.documentation else None
        self.configuration = ConfigurationDto.from_dict(self.configuration) if self.configuration else None
        self.availability = [AvailabilityTimesDto.from_dict(avail_entry) for avail_entry in
                             self.availability] if self.availability else None
        self.costs = [CostDto.from_dict(cost_entry) for cost_entry in self.costs] if self.costs else None

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)
