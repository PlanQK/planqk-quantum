import inspect
from dataclasses import dataclass
from datetime import time, datetime
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional

from planqk.qiskit.client.client_dtos import INPUT_FORMAT


class PROVIDER(Enum):
    AZURE = "AZURE"
    AWS = "AWS"


class TYPE(Enum):
    QPU = "QPU"
    SIMULATOR = "SIMULATOR"
    UNKNOWN = "UNKNOWN"


class HARDWARE_PROVIDER(Enum):
    IONQ = "IONQ"
    RIGETTI = "RIGETTI"
    OQC = "OQC"
    AWS = "AWS"
    AZURE = "AZURE"


class STATUS(Enum):
    """
    STATUS Enum:

    UNKNOWN: The backend status is unknown.
    ONLINE: The backend is online, processing submitted jobs and accepting new ones.
    PAUSED: The backend is accepting jobs, but not currently processing them.
    OFFLINE: The backend is not accepting new jobs, e.g. due to maintenance.
    RETIRED: The backend is not available for use anymore.
    """
    UNKNOWN = "UNKNOWN"
    ONLINE = "ONLINE"
    PAUSED = "PAUSED"
    OFFLINE = "OFFLINE"
    RETIRED = "RETIRED"


@dataclass
class DocumentationDto:
    description: Optional[str] = None
    url: Optional[str] = None
    #status_url: Optional[str] = None
    location: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict): #TODO das auf alle inits anwenden
        init_params = inspect.signature(cls.__init__).parameters
        valid_data = {k: v for k, v in data.items() if k in init_params}
        return cls(**valid_data)


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
        return cls(**data)


@dataclass
class ConnectivityDto:
    fully_connected: bool
    graph: Optional[Dict[str, List[str]]] = None

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


@dataclass
class ShotsRangeDto:
    min: int
    max: int

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


@dataclass
class ConfigurationDto:
    gates: List[GateDto]
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
        return cls(**data)


class CostGranularity(Enum):
    SHOT = "SHOT"
    JOB = "JOB"


@dataclass
class CostDto:
    granularity: CostGranularity
    currency: str
    value: float

    def __post_init__(self):
        self.granularity = CostGranularity(self.granularity)

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


@dataclass
class BackendDto:
    id: str
    internal_id: str
    provider: PROVIDER
    hardware_provider: HARDWARE_PROVIDER
    name: str
    documentation: DocumentationDto
    configuration: ConfigurationDto
    type: TYPE
    status: STATUS
    availability: List[AvailabilityTimesDto]
    costs: List[CostDto]
    updated_at: datetime
    avg_queue_time: Optional[int] = None

    def __post_init__(self):
        self.provider = PROVIDER(self.provider)
        self.hardware_provider = HARDWARE_PROVIDER(self.hardware_provider)
        self.type = TYPE(self.type)
        self.status = STATUS(self.status)
        self.documentation = DocumentationDto.from_dict(self.documentation)
        self.configuration = ConfigurationDto.from_dict(self.configuration)
        #self.availability = ConfigurationDto(self.configuration)

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)
