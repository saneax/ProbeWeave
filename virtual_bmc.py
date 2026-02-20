#!/usr/bin/env python3
import sys
import yaml
import time
from gns3fy import Gns3Connector, Project

class VirtualBMC:
    def __init__(self, project_name="probeweave_test"):
        server_url = "http://localhost:3080"
        user = "admin"
        password = "3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp"
        
        self.connector = Gns3Connector(url=server_url, user=user, cred=password)
        self.project = Project(name=project_name, connector=self.connector)
        try:
            self.project.get()
        except:
            print(f"Project '{project_name}' not found.")
            sys.exit(1)
            
        self.nodes = {node.name: node for node in self.project.nodes}

    def power_on(self, node_name):
        if node_name not in self.nodes:
            return f"Error: Node {node_name} not found."
        node = self.nodes[node_name]
        if node.status != "started":
            node.start()
            return f"Node {node_name} powered ON."
        return f"Node {node_name} is already ON."

    def power_off(self, node_name):
        if node_name not in self.nodes:
            return f"Error: Node {node_name} not found."
        node = self.nodes[node_name]
        if node.status != "stopped":
            node.stop()
            return f"Node {node_name} powered OFF."
        return f"Node {node_name} is already OFF."

    def power_status(self, node_name):
        if node_name not in self.nodes:
            return f"Error: Node {node_name} not found."
        # Refresh status
        self.project.get_nodes()
        node = next((n for n in self.project.nodes if n.name == node_name), None)
        return f"Power State: {node.status.upper()}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ./virtual_bmc.py <power|status> <on|off|status> <node_name>")
        print("Example: ./virtual_bmc.py power on pc-1")
        sys.exit(1)

    cmd_type = sys.argv[1] # power
    action = sys.argv[2]   # on/off/status
    node_name = sys.argv[3]

    bmc = VirtualBMC()
    
    if cmd_type == "power":
        if action == "on":
            print(bmc.power_on(node_name))
        elif action == "off":
            print(bmc.power_off(node_name))
        elif action == "status":
            print(bmc.power_status(node_name))
        else:
            print("Invalid power action. Use on/off/status.")
    else:
        print("Unknown command. Only 'power' implemented.")
