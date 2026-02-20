from gns3fy import Gns3Connector
import json

server_url = "http://localhost:3080"
user = "admin"
password = "3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp"

connector = Gns3Connector(url=server_url, user=user, cred=password)

try:
    print(f"Server version: {connector.get_version()}")
    projects = connector.get_projects()
    print(f"Projects: {[p['name'] for p in projects]}")
except Exception as e:
    print(f"Error: {e}")
