import dataclasses
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Set, Union, List
import json
from enum import Enum

from pydantic import validator

from planqk.qiskit.client.dto_utils import init_with_defined_params


class INPUT_FORMAT(str, Enum):
    OPEN_QASM_V3 = "OPEN_QASM_V3"
    IONQ_CIRCUIT_V1 = "IONQ_CIRCUIT_V1"


class JOB_STATUS(str, Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"


@dataclass
class JobDto:
    backend_id: str
    provider: str
    shots: int = 1
    id: Optional[str] = None
    input: Optional[Union[str, Dict]] = None
    input_format: Optional[INPUT_FORMAT] = None
    input_params: Optional[Dict] = None
    begin_execution_time: Optional[str] = None
    cancellation_time: Optional[str] = None
    creation_time: Optional[str] = None
    end_execution_time: Optional[str] = None
    error_data: Optional[dict] = None
    metadata: Optional[Dict[str, str]] = None
    name: Optional[str] = None
    status: Optional[JOB_STATUS] = None
    tags: Optional[Set[str]] = None

    #TODO make me extensible

    def __post_init__(self):
        if self.error_data is not None and isinstance(self.error_data, str):
            self.error_data = json.loads(self.error_data)
        if self.input_params is not None and isinstance(self.input_params, str):
            self.input_params = json.loads(self.input_params)

    @classmethod
    def from_dict(cls, data: Dict):
        return init_with_defined_params(cls, data)

    def to_dict(self):
        return asdict(self)


@dataclass
class JobResultDto:
    counts: Dict[str, int]
    memory: List[str]

    @classmethod
    def from_dict(cls, data: Dict):
        # Validate that just bitrings were provided
        counts = data.get("counts", {})
        for key in counts.keys():
            if not cls.is_bitstring(key):
                raise ValueError(f"{key} is not a valid bitstring")

        memory = data.get("memory", [])
        for mem in memory:
            if not cls.is_bitstring(mem):
                raise ValueError(f"{mem} is not a valid bitstring")

        return init_with_defined_params(cls, data)

    @staticmethod
    def is_bitstring(s: str) -> bool:
        return set(s).issubset('01')

