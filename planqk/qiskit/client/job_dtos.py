import json
from enum import Enum
from typing import Optional, Dict, Set, Union

from pydantic import BaseModel


class INPUT_FORMAT(str, Enum):
    OPEN_QASM_V3 = "OPEN_QASM_V3"
    IONQ_CIRCUIT_V1 = "IONQ_CIRCUIT_V1"
    QISKIT_PRIMITIVE = "QISKIT_PRIMITIVE"


class JOB_STATUS(str, Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"


class JobDto(BaseModel):
    backend_id: str
    provider: str
    shots: int = 1
    id: Optional[str] = None
    session_id: Optional[str] = None
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

    def __post_init__(self):
        if self.error_data is not None and isinstance(self.error_data, str):
            self.error_data = json.loads(self.error_data)
        if self.input_params is not None and isinstance(self.input_params, str):
            self.input_params = json.loads(self.input_params)


class RuntimeJobParamsDto(BaseModel):
    program_id: str
    image: Optional[str]
    hgp: Optional[str]
    log_level: Optional[str]
    session_id: Optional[str]
    max_execution_time: Optional[int] = None
    start_session: Optional[bool] = False
    session_time: Optional[int] = None
