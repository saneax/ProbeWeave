#!/usr/bin/env python3
import argparse
import json

from .common.gns3_utils import (
    get_gns3_connector,
    get_project,
    load_infrastructure_config,
)


def get_inventory(project_name="probeweave_test"):
    infra_config = load_infrastructure_config()
    setup_data = infra_config.get('setup', {})
    extra_config = {n['name']: n for n in setup_data.get('nodes', [])}

    connector = get_gns3_connector()
    project = get_project(connector, project_name)

    inventory = {
        '_meta': {'hostvars': {}},
        'all': {'children': ['ungrouped']},
        'ungrouped': {'hosts': []}
    }

    for node in project.nodes:
        group = node.node_type
        if group not in inventory:
            inventory[group] = {'hosts': []}
            inventory['all']['children'].append(group)

        inventory[group]['hosts'].append(node.name)

        hostvars = {
            'gns3_node_id': node.node_id,
            'gns3_status': node.status,
            'ansible_host': 'localhost',
            'gns3_console_port': node.console
        }

        if node.name in extra_config:
            for k, v in extra_config[node.name].items():
                if k not in ['name', 'template', 'groups']:
                    hostvars[k] = v

        inventory['_meta']['hostvars'][node.name] = hostvars

    return inventory

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()

    if args.list:
        print(json.dumps(get_inventory(), indent=2))
