import os

import requests

from .credentials import DefaultCredentialsProvider
from .exceptions import PlanqkClientError


def base_url():
    return os.environ.get('PLANQK_QUANTUM_BASE_URL', 'http://127.0.0.1:8000')


class PlanqkClient(object):

    def __init__(self, credentials: DefaultCredentialsProvider):
        self.credentials = credentials

    def get_backends(self) -> list[str]:
        headers = self._get_default_headers()
        response = requests.get(f'{base_url()}/backends', headers=headers)
        if not response:
            raise PlanqkClientError(f'Error requesting available quantum backends (status: {response.status_code})')
        return response.json()

    def submit_job(self, payload: dict) -> dict:
        headers = self._get_default_headers()
        response = requests.post(f'{base_url()}/jobs', json=payload, headers=headers)
        if not response:
            raise PlanqkClientError(f'Error submitting job (status: {response.status_code})')
        return response.json()

    def get_job(self, job_id: str) -> dict:
        headers = self._get_default_headers()
        response = requests.get(f'{base_url()}/jobs/{job_id}', headers=headers)
        if not response:
            raise PlanqkClientError(f'Error requesting details of job "{job_id}" (status: {response.status_code})')
        return response.json()

    def get_job_result(self, job_id: str) -> dict:
        headers = self._get_default_headers()
        response = requests.get(f'{base_url()}/jobs/{job_id}/result', headers=headers)
        if not response:
            raise PlanqkClientError(f'Error requesting result of job "{job_id}" (status: {response.status_code})')
        return response.json()

    def _get_default_headers(self):
        return {'X-Access-Token': self.credentials.get_access_token()}
