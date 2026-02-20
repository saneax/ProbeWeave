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

## Quick Start

### 1. Provision & Crawl
```bash
# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Provision the GNS3 Lab
python3 -m probeweave.provisioner

# Bootstrap Networking/SSH
python3 -m probeweave.bootstrapper

# Run the ProbeWeave Crawler
ansible-playbook -i src/probeweave/inventory.py site.yml
```

### 2. Testing & Quality
We use `tox` to run the test suite across multiple environments and `ruff` for linting.

```bash
# Run all tests and linters
tox

# Run only linting
tox -e lint
```

## Features
- **GNS3 Integration**: Automated topology building from YAML.
- **Serial Bootstrap**: Injects network config without pre-existing SSH.
- **Dynamic Inventory**: Bridges GNS3 state directly to Ansible.
- **IPMI Simulation**: Virtual BMC for power management testing.
- **Jenkins Ready**: Complete pipeline for remote AlmaLinux slaves.

## Infrastructure Blueprint (`infrastructure.yml`)
Describe your entire datacenter in YAML:
```yaml
setup:
  project_name: "probeweave_test"
  nodes:
    - name: "pc-1"
      template: "Alpine-Linux"
      mgmt_ip: "192.168.122.10"
      mgmt_gateway: "192.168.122.1"
  links:
    - ["switch-1", "Ethernet0", "pc-1", "Ethernet0"]
```
