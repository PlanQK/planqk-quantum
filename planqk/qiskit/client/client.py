import json
import logging
import os
import urllib
from typing import List, Optional
from urllib.parse import quote

import requests

from planqk.credentials import DefaultCredentialsProvider
from planqk.exceptions import PlanqkClientError
from planqk.qiskit.client.client_dtos import JobDto
from planqk.qiskit.client.backend_dtos import BackendDto, PROVIDER

logger = logging.getLogger(__name__)


def base_url():
    return os.environ.get("PLANQK_QUANTUM_BASE_URL", "https://platform.planqk.de/qiskit")


def service_execution_id():
    return os.environ.get("SERVICE_EXECUTION_ID", None)


def _dict_values_to_string(obj_values_dict: dict):
    for key in obj_values_dict:
        obj_value = obj_values_dict[key]
        if not isinstance(obj_value, str):
            str_value = json.dumps(obj_value)
            obj_values_dict[key] = str_value


class _PlanqkClient(object):

    _credentials = None

    @classmethod
    def set_credentials(cls, credentials: DefaultCredentialsProvider):
        cls._credentials = credentials

    @classmethod
    def get_backends(cls, name: Optional[str] = None) -> List[BackendDto]:
        headers = cls._get_default_headers()

        params = {}
        if name is not None:
            params["name"] = name

        response = requests.get(f"{base_url()}/backends", params=params, headers=headers)
        if not response:
            raise PlanqkClientError(
                f"Error requesting available quantum backends (HTTP {response.status_code}: {response.text})"
            )
        return [BackendDto.from_dict(backend_info) for backend_info in response.json()]

    @classmethod
    def get_backend(cls, backend_id: str):
        headers = cls._get_default_headers()
        response = requests.get(f"{base_url()}/backends/{backend_id}", headers=headers)
        if not response:
            raise PlanqkClientError(
                f"Error requesting available quantum backends (HTTP {response.status_code}: {response.text})"
            )
        return response.json()

    @classmethod
    def submit_job(cls, job: JobDto) -> str:
        #TODO type job request
        headers = cls._get_default_headers()
        headers["Content-TYPE"] = "application/json"

        job_dict = job.__dict__
        #_dict_values_to_string(job_dict.get("metadata")) TODO in azure

        response = requests.post(f"{base_url()}/jobs", json=job_dict, headers=headers)
        if not response:
            raise PlanqkClientError(f"Error submitting job (HTTP {response.status_code}: {response.text})")
        return response.json()["id"]

    @classmethod
    def get_job(cls, job_id: str) -> JobDto:
        headers = cls._get_default_headers()
        encoded_job_id = urllib.parse.quote_plus(job_id)
        response = requests.get(f"{base_url()}/jobs/{encoded_job_id}", headers=headers)
        if not response:
            raise PlanqkClientError(
                f'Error requesting details of job "{job_id}" (HTTP {response.status_code}: {response.text})'
            )
        return JobDto.from_dict(response.json())

    @classmethod
    def get_job_result(cls, job_id: str) -> dict:
        headers = cls._get_default_headers()
        response = requests.get(f"{base_url()}/jobs/{job_id}/result", headers=headers)
        if not response:
            raise PlanqkClientError(
                f'Error requesting result of job "{job_id}" (HTTP {response.status_code}: {response.text})'
            )
        return response.json()

    @classmethod
    def cancel_job(cls, job_id: str) -> None:
        headers = cls._get_default_headers()
        response = requests.delete(f"{base_url()}/jobs/{job_id}", headers=headers)
        if not response:
            raise PlanqkClientError(
                f'Error cancelling job "{job_id}" (HTTP {response.status_code}: {response.text})'
            )

    @classmethod
    def _get_default_headers(cls):
        headers = {"x-auth-token": cls._credentials.get_access_token()}

        # inject service execution if present
        if service_execution_id() is not None:
            headers["x-planqk-service-execution-id"] = service_execution_id()

        return headers
