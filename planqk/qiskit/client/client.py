import json
import logging
import os
import random
from typing import List, Optional, Callable, Any, Dict

import requests
from requests import Response, HTTPError

from planqk.context import ContextResolver
from planqk.credentials import DefaultCredentialsProvider
from planqk.exceptions import InvalidAccessTokenError, PlanqkClientError, PlanqkError
from planqk.qiskit.client.backend_dtos import BackendDto, PROVIDER, BackendStateInfosDto
from planqk.qiskit.client.job_dtos import JobDto

HEADER_CLOUD_TRACE_CTX = "x-cloud-trace-context"

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
    _context_resolver: ContextResolver = None

    @classmethod
    def set_credentials(cls, credentials: DefaultCredentialsProvider):
        cls._credentials = credentials

    @classmethod
    def get_credentials(cls):
        return cls._credentials

    @classmethod
    def set_organization_id(cls, organization_id: str):
        cls._organization_id = organization_id

    @classmethod
    def perform_request(cls, request_func: Callable[..., Response], url: str, params=None, data=None, headers=None):
        headers = {**cls._get_default_headers(), **(headers or {})}
        debug = os.environ.get("PLANQK_QUANTUM_DEBUG", "false").lower() == "true"

        trace_id = headers.get(HEADER_CLOUD_TRACE_CTX, 'unknown')
        try:
            response = request_func(url, json=data, params=params, headers=headers, verify=not debug)
            response.raise_for_status()
            return response.json() if response.status_code != 204 else None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to middleware under {url} (Trace {trace_id}): {e}")
            raise e
        except HTTPError as e:
            logger.error(f"Request {request_func.__name__} {url} failed (Trace {trace_id}): {e}")
            if e.response.status_code == 401:
                raise InvalidAccessTokenError
            else:
                raise PlanqkClientError(e.response)
        except Exception as e:
            logger.error(f"Request {request_func.__name__} {url} failed (Trace {trace_id}): {e}")
            raise PlanqkError("Error while performing request") from e

    @classmethod
    def get_backends(cls) -> List[BackendDto]:
        headers = {}
        params = {"onlyQiskit": True}

        response = cls.perform_request(requests.get, f"{base_url()}/backends", params=params, headers=headers)

        return [BackendDto(**backend_info) for backend_info in response]

    @classmethod
    def get_backend(cls, backend_id: str) -> BackendDto:
        headers = {}

        response = cls.perform_request(requests.get, f"{base_url()}/backends/{backend_id}", headers=headers)
        return BackendDto(**response)

    @classmethod
    def get_backend_state(cls, backend_id: str) -> BackendStateInfosDto:
        headers = {}

        response = cls.perform_request(requests.get, f"{base_url()}/backends/{backend_id}/status", headers=headers)
        return BackendStateInfosDto(**response)

    @classmethod
    def submit_job(cls, job: JobDto) -> JobDto:
        headers = {"content-type": "application/json"}

        # Create dict from job object and remove attributes with None values from it
        job_dict = cls.remove_none_values(job.__dict__)

        response = cls.perform_request(requests.post, f"{base_url()}/jobs", data=job_dict, headers=headers)
        return JobDto(**response)

    @classmethod
    def get_job(cls, job_id: str, provider: Optional[PROVIDER] = None) -> JobDto:
        params = {}
        if provider is not None:
            params["provider"] = provider.name

        response = cls.perform_request(requests.get, f"{base_url()}/jobs/{job_id}", params=params)
        return JobDto(**response)

    @classmethod
    def get_jobs(cls) -> List[JobDto]:
        response = cls.perform_request(requests.get, f"{base_url()}/jobs")
        return [JobDto(**job_info) for job_info in response]

    @classmethod
    def get_job_result(cls, job_id: str, provider: Optional[PROVIDER] = None) -> Dict[str, Any]:
        params = {}
        if provider is not None:
            params["provider"] = provider.name

        response = cls.perform_request(requests.get, f"{base_url()}/jobs/{job_id}/result", params=params)
        return response

    @classmethod
    def cancel_job(cls, job_id: str, provider: Optional[PROVIDER] = None) -> None:
        params = {}
        if provider is not None:
            params["provider"] = provider.name

        cls.perform_request(requests.delete, f"{base_url()}/jobs/{job_id}", params=params)

    @classmethod
    def _get_default_headers(cls):
        headers = {"x-auth-token": cls._credentials.get_access_token()}

        # inject service execution if present
        if service_execution_id() is not None:
            headers["x-planqk-service-execution-id"] = service_execution_id()

        if cls._context_resolver is None:
            cls._context_resolver = ContextResolver()

        context = cls._context_resolver.get_context()

        if cls._organization_id is not None:
            headers["x-organizationid"] = cls._organization_id
        elif context is not None and context.is_organization:
            headers["x-organizationid"] = context.get_organization_id()

        headers[HEADER_CLOUD_TRACE_CTX] = cls._generate_trace_id()
        logger.debug("PlanQK client request trace id: %s", headers[HEADER_CLOUD_TRACE_CTX])

        return headers

    @classmethod
    def remove_none_values(cls, d):
        if not isinstance(d, dict):
            return d
        return {k: cls.remove_none_values(v) for k, v in d.items() if v is not None}

    @classmethod
    def _generate_trace_id(cls):
        return '{:032x}'.format(random.getrandbits(128))
