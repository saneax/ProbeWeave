#!/home/sanjayu/shelf/projects/ProbeWeave/.venv/bin/python3
import socket
import sys
import time
import json
import yaml
from gns3fy import Gns3Connector, Project

class NodeBootstrapper:
    def __init__(self, project_name="probeweave_test"):
        server_url = "http://localhost:3080"
        user = "admin"
        password = "3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp"
        
        self.connector = Gns3Connector(url=server_url, user=user, cred=password)
        self.project = Project(name=project_name, connector=self.connector)
        try:
            self.project.get()
        except:
            print("Project not found")

    def send_cmd(self, sock, cmd):
        print(f"Sending: {cmd}")
        sock.sendall(cmd.encode('ascii') + b"\n")
        time.sleep(0.5)
        try:
            return sock.recv(4096).decode('ascii', errors='ignore')
        except socket.timeout:
            return ""

    def configure_node(self, node_name, config):
        # Find node console port
        self.project.get_nodes()
        node = next((n for n in self.project.nodes if n.name == node_name), None)
        if not node:
            print(f"Node {node_name} not found.")
            return

        host = "localhost"
        port = node.console
        print(f"Connecting to {node_name} on {host}:{port}...")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((host, port))
            
            # Wake up console
            sock.sendall(b"\n")
            time.sleep(1)
            
            # Check for login prompt
            try:
                data = sock.recv(1024).decode('ascii', errors='ignore')
                if "login:" in data:
                    print("Logging in as root...")
                    sock.sendall(b"root\n")
                    time.sleep(1)
            except socket.timeout:
                pass
            
            # Setup network commands
            # Using 'setup-interfaces' is interactive, so we manually edit files or run ip commands
            # We will use 'ip' commands for immediate effect and persistence in /etc/network/interfaces
            
            cmds = [
                # Configure Interface
                f"ip addr add {config.get('mgmt_ip')}/24 dev eth0",
                f"ip link set eth0 up",
                f"ip route add default via {config.get('mgmt_gateway')}",
                "echo 'nameserver 8.8.8.8' > /etc/resolv.conf",
                
                # Install packages (assuming internet access via NAT/Gateway)
                "apk update",
                "apk add python3 openssh",
                
                # Configure SSH
                "sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config",
                "rc-service sshd start",
                "rc-update add sshd",
                
                # Set password
                "echo 'root:password' | chpasswd"
            ]

            for cmd in cmds:
                self.send_cmd(sock, cmd)
                
            sock.close()
            print(f"Configuration complete for {node_name}.")
            
        except Exception as e:
            print(f"Failed to configure {node_name}: {e}")

if __name__ == "__main__":
    bootstrapper = NodeBootstrapper()
    
    # Load config from infrastructure.yml
    with open("infrastructure.yml", 'r') as f:
        config = yaml.safe_load(f)
        
    setup = config.get('setup', {})
    nodes_cfg = setup.get('nodes', [])
    
    for node_cfg in nodes_cfg:
        if 'mgmt_ip' in node_cfg:
            bootstrapper.configure_node(node_cfg['name'], node_cfg)
