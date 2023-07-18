import os
from abc import ABC

from dwave.cloud import Client
from dwave.samplers import SimulatedAnnealingSampler
from dwave.system import LeapHybridSampler, DWaveSampler, DWaveCliqueSampler, LeapHybridCQMSampler, LeapHybridDQMSampler

from planqk.credentials import DefaultCredentialsProvider


class Sampler(ABC):
    def __init__(self, cls: type, **config):
        self._cls = cls
        self._config = config
        self.name = cls.__name__

    def __call__(self, **config):
        config = {**self._config, **config}
        return self._cls(**config)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return str(self)


SUPPORTED_SAMPLERS = [
    # samplers from dwave-samplers package
    # https://docs.ocean.dwavesys.com/en/stable/docs_samplers/index.html
    Sampler(SimulatedAnnealingSampler),
    # samplers from dwave-system package
    # https://docs.ocean.dwavesys.com/en/stable/docs_system/sdk_index.html
    Sampler(DWaveSampler),
    Sampler(DWaveCliqueSampler),
    Sampler(LeapHybridSampler),
    Sampler(LeapHybridCQMSampler),
    Sampler(LeapHybridDQMSampler),
]


class PlanqkDwaveProvider(ABC):
    def __init__(self, access_token=None):
        self._credentials_provider = DefaultCredentialsProvider(access_token)
        self._supported_samplers = SUPPORTED_SAMPLERS
        self._samplers_dict = {v.name: v for v in self._supported_samplers}

        # TODO: change DWAVE_ENDPOINT variable name to PLANQK_DWAVE_ENDPOINT
        endpoint = os.environ.get("DWAVE_ENDPOINT", "https://platform.planqk.de/dwave/sapi/v2")
        os.environ["DWAVE_API_ENDPOINT"] = endpoint
        os.environ["DWAVE_API_TOKEN"] = self._credentials_provider.get_access_token()

        # TODO: prefix SERVICE_EXECUTION_ID with PLANQK_
        service_execution_id = os.environ.get("SERVICE_EXECUTION_ID", "None")
        os.environ["DWAVE_API_HEADERS"] = f"x-planqk-service-execution-id: {service_execution_id}"

    def supported_samplers(self):
        return self._supported_samplers

    def get_sampler(self, name: str, **config):
        sampler = self._samplers_dict.get(name)
        if sampler is None:
            # list of samplers to str
            supported_samplers = [str(s) for s in self._supported_samplers]
            supported_samplers = ", ".join(supported_samplers)
            raise ValueError(f"Sampler '{name}' not supported. Supported samplers: {supported_samplers}")
        return sampler(**config)

    @staticmethod
    def get_solvers(refresh=False, order_by='avg_load', **filters):
        client = Client.from_config()
        return client.get_solvers(refresh, order_by, **filters)
