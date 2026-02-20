import pytest
import requests
import socket
from probeweave.common.gns3_utils import get_gns3_connector, load_infrastructure_config

def test_gns3_server_reachable():
    """Verify GNS3 Server is up and responding."""
    connector = get_gns3_connector()
    version = connector.get_version()
    assert "version" in version

def test_project_provisioned():
    """Verify the project exists in GNS3."""
    connector = get_gns3_connector()
    projects = [p['name'] for p in connector.get_projects()]
    assert "probeweave_test" in projects

def test_nodes_running():
    """Verify nodes are in 'started' state."""
    connector = get_gns3_connector()
    projects = connector.get_projects()
    project_id = next(p['project_id'] for p in projects if p['name'] == "probeweave_test")
    
    nodes = connector.get_nodes(project_id)
    for node in nodes:
        if node['name'] in ['pc-1', 'pc-2']:
            assert node['status'] == "started"

def test_ssh_connectivity():
    """Verify SSH is reachable on the configured management IPs."""
    config = load_infrastructure_config()
    nodes = config.get('setup', {}).get('nodes', [])
    for node in nodes:
        if 'mgmt_ip' in node:
            ip = node['mgmt_ip']
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((ip, 22))
            s.close()
            assert result == 0, f"SSH port 22 not reachable on {ip}"
