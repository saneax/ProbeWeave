import sys
import time

from gns3fy import Project

from .common.gns3_utils import get_gns3_connector, load_infrastructure_config


def provision(config_path="infrastructure.yml"):
    config = load_infrastructure_config(config_path)
    setup = config.get('setup', {})
    project_name = setup.get('project_name', 'probeweave_test')

    connector = get_gns3_connector()

    # Check if project exists
    project = None
    for p in connector.get_projects():
        if p['name'] == project_name:
            project = Project(name=project_name, connector=connector)
            project.get()
            print(f"Project '{project_name}' already exists.")
            break

    if not project:
        print(f"Creating project '{project_name}'...")
        connector.http_call("post", f"{connector.base_url}/projects", json_data={"name": project_name})
        project = Project(name=project_name, connector=connector)
        project.get()

    if project.status != "opened":
        project.open()

    existing_nodes = {n.name: n for n in project.nodes}
    for node_cfg in setup.get('nodes', []):
        name = node_cfg['name']
        template_name = node_cfg['template']

        if name in existing_nodes:
            continue

        print(f"Creating node '{name}' from template '{template_name}'...")
        project.create_node(name=name, template=template_name)

    project.get_nodes()
    node_map = {n.name: n for n in project.nodes}

    for link_cfg in setup.get('links', []):
        n1_name, p1_name, n2_name, p2_name = link_cfg
        try:
            print(f"Connecting {n1_name}:{p1_name} to {n2_name}:{p2_name}...")
            project.create_link(n1_name, p1_name, n2_name, p2_name)
        except Exception as e:
            print(f"Link note: {e}")

    print("Starting all nodes...")
    for node in project.nodes:
        if node.status != "started":
            try:
                node.start()
                time.sleep(1)
            except Exception as e:
                print(f"Warning: Failed to start node '{node.name}': {e}")

    print("Provisioning complete.")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "infrastructure.yml"
    provision(path)
