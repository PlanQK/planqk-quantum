import json
import logging
import os
from typing import List, Optional, Callable

import requests
from requests import Response, HTTPError

from planqk.credentials import DefaultCredentialsProvider
from planqk.exceptions import InvalidAccessTokenError, PlanqkClientError
from planqk.qiskit.client.backend_dtos import BackendDto
from planqk.qiskit.client.client_dtos import JobDto

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
    def perform_request(cls, request_func: Callable[..., Response], url, params=None, data=None, headers=None):
        headers = {**cls._get_default_headers(), **(headers or {})}
        try:
            response = request_func(url, json=data, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to middleware under {url}: {e}")
            raise e
        except HTTPError as e:
            if e.response.status_code == 401:
                raise InvalidAccessTokenError
            else:
                raise PlanqkClientError(e.response)

    @classmethod
    def get_backends(cls, name: Optional[str] = None) -> List[BackendDto]:
        params = {}
        if name is not None:
            params["name"] = name

        response = cls.perform_request(requests.get, f"{base_url()}/backends", params=params)

        return [BackendDto.from_dict(backend_info) for backend_info in response]

    @classmethod
    def get_backend(cls, backend_id: str):
        response = cls.perform_request(requests.get, f"{base_url()}/backends/{backend_id}")
        response.raise_for_status()
        return response.json()

    @classmethod
    def submit_job(cls, job: JobDto) -> str:
        headers = {"content-type": "application/json"}

        job_dict = job.__dict__

        response = cls.perform_request(requests.post, f"{base_url()}/jobs", data=job_dict, headers=headers)
        return response["id"]

    @classmethod
    def get_job(cls, job_id: str) -> JobDto:
        response = cls.perform_request(requests.get, f"{base_url()}/jobs/{job_id}")
        return JobDto.from_dict(response)

    @classmethod
    def get_job_result(cls, job_id: str) -> dict:
        response = cls.perform_request(requests.get, f"{base_url()}/jobs/{job_id}/result")
        return response

    @classmethod
    def cancel_job(cls, job_id: str) -> None:
        cls.perform_request(requests.delete, f"{base_url()}/jobs/{job_id}")

    @classmethod
    def _get_default_headers(cls):
        headers = {"x-auth-token": cls._credentials.get_access_token()}

        # inject service execution if present
        if service_execution_id() is not None:
            headers["x-planqk-service-execution-id"] = service_execution_id()

        return headers
