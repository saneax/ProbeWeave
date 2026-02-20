#!/home/sanjayu/shelf/projects/ProbeWeave/.venv/bin/python3
import sys
from gns3fy import Gns3Connector, Project

def cleanup(project_name="probeweave_test"):
    server_url = "http://localhost:3080"
    user = "admin"
    password = "3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp"
    
    connector = Gns3Connector(url=server_url, user=user, cred=password)
    
    try:
        # Get all projects
        projects = connector.get_projects()
        target_project = next((p for p in projects if p['name'] == project_name), None)
        
        if target_project:
            print(f"Found existing project '{project_name}' (ID: {target_project['project_id']}). Deleting...")
            project = Project(name=project_name, connector=connector)
            project.get()
            # Stop all nodes first to be safe
            for node in project.nodes:
                if node.status != "stopped":
                    node.stop()
            project.delete()
            print("Project deleted successfully.")
        else:
            print(f"No existing project named '{project_name}' found. Clean slate.")
            
    except Exception as e:
        print(f"Cleanup note: {e} (This is normal if the server was just installed)")

if __name__ == "__main__":
    p_name = "probeweave_test"
    if len(sys.argv) > 1:
        p_name = sys.argv[1]
    cleanup(p_name)
