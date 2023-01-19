import json
import logging
import os

import requests

from .credentials import DefaultCredentialsProvider
from .exceptions import PlanqkClientError

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


class PlanqkClient(object):

    def __init__(self, credentials: DefaultCredentialsProvider):
        self.credentials = credentials

    def get_backends(self):
        headers = self._get_default_headers()
        response = requests.get(f"{base_url()}/backends", headers=headers)
        if not response:
            raise PlanqkClientError(
                f"Error requesting available quantum backends (HTTP {response.status_code}: {response.text})"
            )
        return response.json()

    def submit_job(self, job) -> dict:
        headers = self._get_default_headers()
        headers["Content-Type"] = "application/json"

        job_dict = job.to_dict()
        _dict_values_to_string(job_dict.get("metadata"))

        response = requests.post(f"{base_url()}/jobs", json=job_dict, headers=headers)
        if not response:
            raise PlanqkClientError(f"Error submitting job (HTTP {response.status_code}: {response.text})")
        return response.json()

    def get_job(self, job_id: str) -> dict:
        headers = self._get_default_headers()
        response = requests.get(f"{base_url()}/jobs/{job_id}", headers=headers)
        if not response:
            raise PlanqkClientError(
                f'Error requesting details of job "{job_id}" (HTTP {response.status_code}: {response.text})'
            )
        return response.json()

    def get_job_result(self, job_id: str) -> dict:
        headers = self._get_default_headers()
        response = requests.get(f"{base_url()}/jobs/{job_id}/result", headers=headers)
        if not response:
            raise PlanqkClientError(
                f'Error requesting result of job "{job_id}" (HTTP {response.status_code}: {response.text})'
            )
        return response.json()

    def cancel_job(self, job_id: str) -> None:
        headers = self._get_default_headers()
        response = requests.delete(f"{base_url()}/jobs/{job_id}", headers=headers)
        if not response:
            raise PlanqkClientError(
                f'Error cancelling job "{job_id}" (HTTP {response.status_code}: {response.text})'
            )

    def _get_default_headers(self):
        headers = {"x-auth-token": self.credentials.get_access_token()}

        # inject service execution if present
        if service_execution_id() is not None:
            headers["x-planqk-service-execution-id"] = service_execution_id()

        return headers
