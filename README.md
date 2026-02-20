# ProbeWeave — GNS3-Native System Crawler

Agentless system crawler that gathers deep hardware/software/app facts using Ansible roles and GNS3 simulation.

## Project Structure

```
├── src/probeweave/       # Application Suite
│   ├── common/           # Shared GNS3 & Config utilities
│   ├── provisioner.py    # GNS3 Topology Builder
│   ├── bootstrapper.py   # Serial Console Configurator
│   ├── inventory.py      # Dynamic Ansible Inventory
│   └── ...
├── tests/                # Test Suite
├── roles/                # Ansible Roles (Crawl Logic)
├── infrastructure.yml    # Datacenter Blueprint (YAML)
├── Jenkinsfile           # CI/CD Orchestration
└── tox.ini               # Test & Lint Automation
```

## Advanced Example: Dual-NIC Datacenter
ProbeWeave can provision complex topologies with segmented networks. Below is an example with a private LAN and a dedicated Cloud/Management network.

### `infrastructure.yml`
```yaml
setup:
  project_name: "probeweave_datacenter"
  nodes:
    - name: "lan-switch"
      template: "Ethernet switch"
    - name: "cloud-switch"
      template: "Ethernet switch"
    - name: "nat-gw"
      template: "NAT"

    - name: "compute-01"
      template: "Alpine-Linux"
      mgmt_ip: "192.168.122.10"
      mgmt_interface: "eth1"
      mgmt_gateway: "192.168.122.1"

  links:
    # Internal Traffic (NIC 0)
    - ["lan-switch", "Ethernet0", "compute-01", "Ethernet0"]
    # Management Traffic (NIC 1)
    - ["cloud-switch", "Ethernet0", "compute-01", "Ethernet1"]
    # Internet Exit
    - ["nat-gw", "nat0", "cloud-switch", "Ethernet7"]
```

## Quick Start

### 1. Provision & Crawl
```bash
# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# 1. Build the GNS3 Lab
python3 -m probeweave.provisioner

# 2. Bootstrap Networking/SSH via Serial Console
python3 -m probeweave.bootstrapper

# 3. Run the ProbeWeave Crawler
ansible-playbook -i src/probeweave/inventory.py site.yml
```

### 2. Testing & Quality
We use `tox` for automated testing and `ruff` for linting.

```bash
# Run all tests and linters
tox

# Run only linting
tox -e lint
```

## Features
- **GNS3-Native**: Automated topology building from YAML.
- **Dual-Stack Support**: Segment management and data traffic at the blueprint level.
- **Serial Bootstrap**: Injects network config and installs SSH without pre-existing access.
- **Dynamic Inventory**: Bridges GNS3 state directly to Ansible.
- **Jenkins Ready**: Complete pipeline for remote AlmaLinux slaves on AWS.
