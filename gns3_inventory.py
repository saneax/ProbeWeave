#!/home/sanjayu/shelf/projects/ProbeWeave/.venv/bin/python3
import json
import sys
import argparse
from gns3fy import Gns3Connector, Project

import yaml
import os

def get_inventory(project_name):
    # Load extra config from infrastructure.yml if available
    extra_config = {}
    infra_path = "/home/sanjayu/shelf/projects/ProbeWeave/infrastructure.yml"
    if os.path.exists(infra_path):
        with open(infra_path, 'r') as f:
            setup_data = yaml.safe_load(f).get('setup', {})
            for node_cfg in setup_data.get('nodes', []):
                extra_config[node_cfg['name']] = node_cfg

    server_url = "http://localhost:3080"
    user = "admin"
    password = "3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp"
    
    connector = Gns3Connector(url=server_url, user=user, cred=password)
    project = Project(name=project_name, connector=connector)
    project.get()
    
    inventory = {
        '_meta': {
            'hostvars': {}
        },
        'all': {
            'children': ['ungrouped']
        },
        'ungrouped': {
            'hosts': []
        }
    }
    
    for node in project.nodes:
        # Determine group
        group = node.node_type
        if group not in inventory:
            inventory[group] = {'hosts': []}
            inventory['all']['children'].append(group)
        
        inventory[group]['hosts'].append(node.name)
        
        # Add hostvars
        hostvars = {
            'gns3_node_id': node.node_id,
            'gns3_project_id': node.project_id,
            'gns3_status': node.status,
            'ansible_host': 'localhost', # Default
            'gns3_console_port': node.console
        }
        
        # Merge extra config from infrastructure.yml
        if node.name in extra_config:
            for k, v in extra_config[node.name].items():
                if k not in ['name', 'template', 'groups']: # Don't overwrite metadata
                    hostvars[k] = v
        
        inventory['_meta']['hostvars'][node.name] = hostvars
        
    return inventory

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host', action='store_true')
    args = parser.parse_args()
    
    # We could get the project name from an env var or config
    project_name = "probeweave_test"
    
    if args.list:
        print(json.dumps(get_inventory(project_name), indent=2))
    elif args.host:
        # Individual host info not implemented for simplicity
        print(json.dumps({}))
    else:
        parser.print_help()
