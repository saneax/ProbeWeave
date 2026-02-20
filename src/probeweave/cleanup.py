from .common.gns3_utils import get_gns3_connector


def cleanup(project_name="probeweave_test"):
    connector = get_gns3_connector()
    try:
        projects = connector.get_projects()
        target = next((p for p in projects if p['name'] == project_name), None)
        if target:
            print(f"Deleting project {project_name}...")
            connector.http_call("delete", f"{connector.base_url}/projects/{target['project_id']}")
    except Exception as e:
        print(f"Cleanup error: {e}")

if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "probeweave_test"
    cleanup(name)
