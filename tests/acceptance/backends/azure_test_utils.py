import os

from azure.identity import ClientSecretCredential
from azure.quantum import Workspace
from azure.quantum.qiskit import AzureQuantumProvider

BACKEND_ID_AZURE_IONQ_HARMONY = "azure.ionq.harmony"
BACKEND_ID_AZURE_IONQ_SIM= "azure.ionq.simulator"

AZURE_NAME_IONQ_HARMONY = "ionq.qpu"
AZURE_NAME_IONQ_SIM = "ionq.simulator"

def init_azure_provider() -> AzureQuantumProvider:
    AZ_TENANT_ID = os.environ.get('AZ_TENANT_ID')
    AZ_CLIENT_ID = os.environ.get('AZ_CLIENT_ID')
    AZ_CLIENT_SECRET = os.environ.get('AZ_CLIENT_SECRET')
    AZ_QUANTUM_RESOURCE_ID = os.environ.get('AZ_QUANTUM_RESOURCE_ID')
    AZ_REGION = os.environ.get('AZ_REGION')

    credential = ClientSecretCredential(tenant_id=AZ_TENANT_ID,
                                        client_id=AZ_CLIENT_ID,
                                        client_secret=AZ_CLIENT_SECRET)

    workspace = Workspace(
        # Format must match
        resource_id=AZ_QUANTUM_RESOURCE_ID,
        location=AZ_REGION,
        credential=credential
    )
    return AzureQuantumProvider(
        workspace=workspace
    )

