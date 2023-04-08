""" This provider bases on the  AWSBraketProvider from the Qiskit Braket SDK
  https://github.com/qiskit-community/qiskit-braket-provider"""
from braket.device_schema.dwave import DwaveDeviceCapabilities
from braket.device_schema.xanadu import XanaduDeviceCapabilities
from braket.device_schema.quera import QueraDeviceCapabilities
from qiskit.providers import ProviderV1
from qiskit_braket_provider import BraketLocalBackend, AWSBraketBackend

from planqk.client import _PlanqkClient
from planqk.qiskit.providers.braket.planqk_aws_device import _PlanqkAwsDevice
from planqk.qiskit.providers.braket.planqk_braket_backend import _PlanqkAWSBraketBackend


#from .braket_backend import _PlanqkAWSBraketBackend, BraketLocalBackend

class _PlanqkAWSBraketProvider(ProviderV1):
    """AWSBraketProvider class for accessing AWS Braket backends.

       Example:
           >>> provider = AWSBraketProvider()
           >>> backends = provider.backends()
           >>> backends
           [BraketBackend[Aspen-10],
            BraketBackend[Aspen-11],
            BraketBackend[Aspen-8],
            BraketBackend[Aspen-9],
            BraketBackend[Aspen-M-1],
            BraketBackend[IonQ Device],
            BraketBackend[Lucy],
            BraketBackend[SV1],
            BraketBackend[TN1],
            BraketBackend[dm1]]
       """

    def __init__(self, client: _PlanqkClient):
        self._client = client

    def backends(self, name=None, **kwargs):

        if kwargs.get("local"):
            return [BraketLocalBackend(name="default")]
        names = [name] if name else None
        devices = _PlanqkAwsDevice.get_devices(names=names, planqk_client=self._client, **kwargs)
        # filter by supported devices
        # gate models are only supported
        supported_devices = [
            d
            for d in devices
            if not isinstance(
                d.properties,
                (
                    DwaveDeviceCapabilities,
                    XanaduDeviceCapabilities,
                    QueraDeviceCapabilities,
                ),
            )
        ]
        backends = []
        for device in supported_devices:
            backends.append(
                _PlanqkAWSBraketBackend(
                    device=device,
                    provider=self,
                    name=device.name,
                    description=f"AWS Device: {device.provider_name} {device.name}.",
                    online_date=device.properties.service.updatedAt,
                    backend_version="2",
                )
            )
        return backends
