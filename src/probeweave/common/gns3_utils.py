import os

import yaml
from gns3fy import Gns3Connector, Project


def get_gns3_connector():
    """Returns a GNS3 connector using standard credentials."""
    # In a real scenario, these could come from environment variables
    server_url = os.environ.get("GNS3_URL", "http://localhost:3080")
    user = os.environ.get("GNS3_USER", "admin")
    password = os.environ.get("GNS3_PASS", "3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp")

    return Gns3Connector(url=server_url, user=user, cred=password)

def get_project(connector, project_name="probeweave_test"):
    """Retrieves a GNS3 project by name."""
    project = Project(name=project_name, connector=connector)
    project.get()
    return project

def load_infrastructure_config(path="infrastructure.yml"):
    """Loads the infrastructure YAML configuration."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f)
