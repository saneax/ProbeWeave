
# ProbeWeave — Ansible-native starter

Agentless system crawler that gathers deep hardware/software/app facts using plain Ansible roles.
Artifacts are written to `output/` on the control node.

## Quick start

```bash
cd /mnt/data/probeweave-ansible
ansible-playbook site.yml
```

### Run only hardware LLDP + aggregate
```bash
ansible-playbook site.yml -t hardware,aggregate
```

### Disable OpenStack plugin
```bash
ansible-playbook site.yml -e probeweave_plugins_enabled.app_openstack=false
```

## Layout
```
inventories/
group_vars/
roles/
  probeweave.hardware_lldp/
  probeweave.software_os/
  probeweave.app_openstack/
  probeweave.aggregate/
output/
```
