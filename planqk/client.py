import os

import requests

from .credentials import DefaultCredentialsProvider
from .exceptions import PlanqkClientError


def base_url():
    return os.environ.get('PLANQK_QUANTUM_BASE_URL', 'https://quantum-engine.platform.planqk.de')


class PlanqkJob(object):
    def __init__(self, id: str, name: str, target: str, meta_data: dict, input_data: str,
                 input_data_format: str, input_params: dict,
                 provider_id: str, output_data_format: str, begin_execution_time: str,
                 end_execution_time: str, cancellation_time: str, creation_time: str,
                 status: str):
        # def __init__(self, id: str, **kwargs):
        self.id = id
        self.name = name
        self.inputData = input_data
        self.inputDataFormat = input_data_format
        self.inputParams = input_params
        self.providerId = provider_id
        self.target = target
        self.metaData = meta_data
        self.outputDataFormat = output_data_format
        self.beginExecutionTime = begin_execution_time
        self.endExecutionTime = end_execution_time
        self.cancellationTime = cancellation_time
        self.creationTime = creation_time
        self.status = status


class PlanqkClient(object):

    def __init__(self, credentials: DefaultCredentialsProvider):
        self.credentials = credentials

    def get_backends(self):
        headers = self._get_default_headers()
        response = requests.get(f'{base_url()}/backends', headers=headers)
        if not response:
            raise PlanqkClientError(
                f'Error requesting available quantum backends (HTTP {response.status_code}: {response.text})'
            )
        return response.json()

    def submit_job(self, job: PlanqkJob) -> dict:
        headers = self._get_default_headers()
        headers["Content-Type"] = "application/json"
        response = requests.post(f'{base_url()}/jobs', json=vars(job), headers=headers)
        if not response:
            raise PlanqkClientError(f'Error submitting job (HTTP {response.status_code}: {response.text})')
        return response.json()

    def get_job(self, job_id: str) -> PlanqkJob:
        headers = self._get_default_headers()
        response = requests.get(f'{base_url()}/jobs/{job_id}', headers=headers)
        if not response:
            raise PlanqkClientError(
                f'Error requesting details of job "{job_id}" (HTTP {response.status_code}: {response.text})'
            )
        body = response.json()

        job = PlanqkJob(
            id=job_id,
            name=body['name'],
            input_params=body['inputParams'],
            input_data=body.get('inputData', None),
            input_data_format=body.get('inputDataFormat', None),
            output_data_format=body['outputDataFormat'],
            provider_id=body['providerId'],
            target=body['target'],
            meta_data=body['metadata'],
            begin_execution_time=body.get('beginExecutionTime', None),
            end_execution_time=body.get('endExecutionTime', None),
            cancellation_time=body.get('cancellationTime', None),
            creation_time=body.get('creationTime', None),
            status=body.get('status', None))
        return job

    def get_job_result(self, job_id: str) -> dict:
        headers = self._get_default_headers()
        response = requests.get(f'{base_url()}/jobs/{job_id}/result', headers=headers)
        if not response:
            raise PlanqkClientError(
                f'Error requesting result of job "{job_id}" (HTTP {response.status_code}: {response.text})'
            )
        return response.json()

    def cancel_job(self, job_id: str) -> PlanqkJob:
        pass

    def _get_default_headers(self):
        return {'X-Access-Token': self.credentials.get_access_token()}
