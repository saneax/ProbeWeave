import pytest
import requests
import socket
import yaml
import os

# Configuration
SERVER_URL = "http://localhost:3080/v2"
AUTH = ("admin", "3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp")

def test_gns3_server_reachable():
    """Verify GNS3 Server is up and responding."""
    response = requests.get(f"{SERVER_URL}/version", auth=AUTH)
    assert response.status_code == 200
    assert "version" in response.json()

def test_project_provisioned():
    """Verify the project and nodes exist in GNS3."""
    response = requests.get(f"{SERVER_URL}/projects", auth=AUTH)
    projects = [p['name'] for p in response.json()]
    assert "probeweave_test" in projects

def test_nodes_running():
    """Verify all nodes defined in infrastructure.yml are in 'started' state."""
    # Get project ID
    resp = requests.get(f"{SERVER_URL}/projects", auth=AUTH)
    project_id = next(p['project_id'] for p in resp.json() if p['name'] == "probeweave_test")
    
    # Get nodes
    resp = requests.get(f"{SERVER_URL}/projects/{project_id}/nodes", auth=AUTH)
    nodes = resp.json()
    for node in nodes:
        if node['name'] in ['pc-1', 'pc-2']:
            assert node['status'] == "started", f"Node {node['name']} is not started"

def test_ssh_connectivity():
    """Verify SSH is reachable on the configured management IPs."""
    with open("infrastructure.yml", 'r') as f:
        config = yaml.safe_load(f)
    
    nodes = config['setup']['nodes']
    for node in nodes:
        if 'mgmt_ip' in node:
            ip = node['mgmt_ip']
            # Simple socket check for port 22
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            result = s.connect_ex((ip, 22))
            s.close()
            assert result == 0, f"SSH not reachable on {ip}"
