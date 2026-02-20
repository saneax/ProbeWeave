import yaml
from gns3fy import Gns3Connector, Project, Node, Link
import sys
import time

def provision(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    setup = config.get('setup', {})
    project_name = setup.get('project_name', 'ProbeWeave_Lab')
    
    server_url = "http://localhost:3080"
    user = "admin"
    password = "3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp"
    
    connector = Gns3Connector(url=server_url, user=user, cred=password)
    
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
        # Workaround for pydantic issue in gns3fy
        connector.http_call("post", f"{connector.base_url}/projects", json_data={"name": project_name})
        project = Project(name=project_name, connector=connector)
        project.get()
    
    if project.status != "opened":
        project.open()
        
    # Create nodes
    existing_nodes = {n.name: n for n in project.nodes}
    for node_cfg in setup.get('nodes', []):
        name = node_cfg['name']
        template_name = node_cfg['template']
        
        if name in existing_nodes:
            print(f"Node '{name}' already exists.")
            continue
            
        print(f"Creating node '{name}' from template '{template_name}'...")
        # Find template
        template = connector.get_template(name=template_name)
        if not template:
            print(f"Error: Template '{template_name}' not found!")
            continue
            
        project.create_node(name=name, template=template_name)
    
    # Refresh nodes
    project.get_nodes()
    node_map = {n.name: n for n in project.nodes}
    
    # Create links
    # links: [ ["node1", "port1", "node2", "port2"], ... ]
    for link_cfg in setup.get('links', []):
        n1_name, p1_name, n2_name, p2_name = link_cfg
        
        if n1_name not in node_map or n2_name not in node_map:
            print(f"Error: One of the nodes {n1_name} or {n2_name} not found for link.")
            continue
            
        try:
            print(f"Connecting {n1_name}:{p1_name} to {n2_name}:{p2_name}...")
            # Use node_map directly to get node IDs
            project.create_link(n1_name, p1_name, n2_name, p2_name)
        except Exception as e:
            if "already used" in str(e).lower() or "already exist" in str(e).lower():
                print(f"Link {n1_name}:{p1_name} <-> {n2_name}:{p2_name} already exists.")
            else:
                print(f"Link creation failed: {e}")

    # Start all nodes
    print("Starting all nodes...")
    for node in project.nodes:
        if node.status != "started":
            try:
                print(f"Starting {node.name}...")
                node.start()
                # Give GNS3 a moment to breathe between starts
                time.sleep(1)
            except Exception as e:
                print(f"Warning: Failed to start node '{node.name}': {e}")
        
    print("Provisioning complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python provision_gns3.py <config.yml>")
        sys.exit(1)
    provision(sys.argv[1])
