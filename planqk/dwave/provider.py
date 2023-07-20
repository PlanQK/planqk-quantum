import os
from abc import ABC

from dwave.cloud import Client
from dwave.samplers import SimulatedAnnealingSampler, TabuSampler
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
    Sampler(TabuSampler),
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
        self._supported_samplers_list = SUPPORTED_SAMPLERS
        self._supported_samplers_dict = {v.name: v for v in self._supported_samplers_list}

        endpoint = os.environ.get("PLANQK_DWAVE_API_ENDPOINT", "https://platform.planqk.de/dwave/sapi/v2")
        os.environ["DWAVE_API_ENDPOINT"] = endpoint
        os.environ["DWAVE_API_TOKEN"] = self._credentials_provider.get_access_token()

    def supported_samplers(self):
        return self._supported_samplers_list

    def get_sampler(self, name: str, **config):
        sampler = self._supported_samplers_dict.get(name)
        if sampler is None:
            supported_samplers = [str(s) for s in self._supported_samplers_list]
            supported_samplers = ", ".join(supported_samplers)
            raise ValueError(f"Sampler '{name}' not supported. Supported samplers: {supported_samplers}.")
        return sampler(**config)

    @staticmethod
    def get_solvers(refresh=False, order_by='avg_load', **filters):
        client = Client.from_config()
        return client.get_solvers(refresh, order_by, **filters)
