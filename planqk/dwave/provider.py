import os
from abc import ABC

from dwave.cloud import Client
from dwave.samplers import SimulatedAnnealingSampler
from dwave.system import LeapHybridSampler

from planqk.credentials import DefaultCredentialsProvider


class DwaveSampler(ABC):
    def __init__(self, id: str, cls, simulator: bool, **config):
        self.id = id
        self._cls = cls
        self.name = cls.__name__
        self._simulator = simulator
        self._config = config

    def is_simulator(self):
        return self._simulator

    def __call__(self, **config):
        config = {**self._config, **config}
        return self._cls(**config)

    def __str__(self):
        return f"{self.name} (id={self.id})"

    def __repr__(self):
        return str(self)


SUPPORTED_SAMPLERS = [
    DwaveSampler("dwave.sim.annealing", SimulatedAnnealingSampler, True),
    DwaveSampler("dwave.leap.hybrid", LeapHybridSampler, False),
]


class PlanqkDwaveProvider(ABC):
    def __init__(self, access_token=None):
        self._credentials_provider = DefaultCredentialsProvider(access_token)
        self._supported_samplers = SUPPORTED_SAMPLERS
        self._samplers_dict = {v.id: v for v in self._supported_samplers}

    def get_config(self):
        # TODO: change DWAVE_ENDPOINT variable name to PLANQK_DWAVE_ENDPOINT
        endpoint = os.environ.get("DWAVE_ENDPOINT", "https://platform.planqk.de/dwave/sapi/v2")
        token = self._credentials_provider.get_access_token()

        config = {
            "endpoint": endpoint,
            "token": token,
        }

        # TODO: prefix SERVICE_EXECUTION_ID with PLANQK_
        service_execution_id = os.environ.get("SERVICE_EXECUTION_ID", None)
        if service_execution_id:
            config["headers"] = {
                "x-planqk-service-execution-id": service_execution_id
            }

        return config

    def supported_samplers(self):
        return self._supported_samplers

    def get_sampler(self, sampler_id: str, **config):
        sampler = self._samplers_dict.get(sampler_id)
        if sampler is None:
            raise ValueError(f"Sampler with name '{sampler_id}' not supported.")
        if not sampler.is_simulator():
            config = {**config, **self.get_config()}
        return sampler(**config)

    def get_solvers(self, refresh=False, order_by='avg_load', **filters):
        config = self.get_config()
        client = Client.from_config(**config)
        return client.get_solvers(refresh, order_by, **filters)
