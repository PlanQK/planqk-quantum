from datetime import time, date
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel

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
            return cls.UNKNOWN


class HARDWARE_PROVIDER(Enum):
    IONQ = "IONQ"
    RIGETTI = "RIGETTI"
    OQC = "OQC"
    AWS = "AWS"
    AZURE = "AZURE"
    IBM = "IBM"
    DWAVE = "DWAVE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, hw_provider_str):
        try:
            return HARDWARE_PROVIDER(hw_provider_str)
        except KeyError:
            return cls.UNKNOWN


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
            return cls.UNKNOWN


class DocumentationDto(BaseModel):
    description: Optional[str] = None
    url: Optional[str] = None
    # status_url: Optional[str] = None
    location: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict):  # TODO das auf alle inits anwenden
        return init_with_defined_params(cls, data)


class QubitDto(BaseModel):
    id: str

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


class GateDto(BaseModel):
    name: str
    native_gate: bool

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


class ConnectivityDto(BaseModel):
    fully_connected: bool
    graph: Optional[Dict[str, List[str]]] = None

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


class ShotsRangeDto(BaseModel):
    min: int
    max: int

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


class ConfigurationDto(BaseModel):
    gates: List[GateDto]
    instructions: List[str]
    qubits: List[QubitDto]
    qubit_count: int
    connectivity: ConnectivityDto
    supported_input_formats: List[INPUT_FORMAT]
    shots_range: ShotsRangeDto
    memory_result_supported: Optional[bool] = False

    def __post_init__(self):
        self.gates = [GateDto.from_dict(gate) for gate in self.gates]
        self.qubits = [QubitDto.from_dict(qubit) for qubit in self.qubits]
        self.connectivity = ConnectivityDto.from_dict(self.connectivity)
        self.supported_input_formats = [INPUT_FORMAT(input_format) for input_format in self.supported_input_formats]
        self.shots_range = ShotsRangeDto.from_dict(self.shots_range)

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


class AvailabilityTimesDto(BaseModel):
    granularity: str
    start: time
    end: time

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


class CostDto(BaseModel):
    granularity: str
    currency: str
    value: float

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


class BackendStateInfosDto(BaseModel):
    status: STATUS
    queue_avg_time: Optional[int] = None
    queue_size: Optional[int] = None
    provider_token_valid: Optional[bool] = None

    def __post_init__(self):
        self.status = STATUS(self.status) if self.status else None

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)


class BackendDto(BaseModel):
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
    updated_at: Optional[date] = None
    avg_queue_time: Optional[int] = None
