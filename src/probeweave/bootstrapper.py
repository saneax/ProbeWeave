import socket
import time

from .common.gns3_utils import (
    get_gns3_connector,
    get_project,
    load_infrastructure_config,
)


class NodeBootstrapper:
    def __init__(self, project_name="probeweave_test"):
        self.connector = get_gns3_connector()
        self.project = get_project(self.connector, project_name)

    def send_cmd(self, sock, cmd):
        print(f"Sending: {cmd}")
        sock.sendall(cmd.encode("ascii") + b"\n")
        time.sleep(0.5)
        try:
            return sock.recv(4096).decode("ascii", errors="ignore")
        except socket.timeout:
            return ""

    def bootstrap(self):
        config = load_infrastructure_config()
        nodes_cfg = config.get("setup", {}).get("nodes", [])

        self.project.get_nodes()
        for node_cfg in nodes_cfg:
            if "mgmt_ip" not in node_cfg:
                continue

            name = node_cfg["name"]
            node = next((n for n in self.project.nodes if n.name == name), None)
            if not node:
                continue

            mgmt_iface = node_cfg.get("mgmt_interface", "eth0")
            print(f"Connecting to {name} on localhost:{node.console}...")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect(("localhost", node.console))
                sock.sendall(b"\n")
                time.sleep(1)

                cmds = [
                    f"ip addr add {node_cfg['mgmt_ip']}/24 dev {mgmt_iface}",
                    f"ip link set {mgmt_iface} up",
                    f"ip route add default via {node_cfg['mgmt_gateway']}",
                    "echo 'nameserver 8.8.8.8' > /etc/resolv.conf",
                    "apk update && apk add python3 openssh",
                    "sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' "
                    "/etc/ssh/sshd_config",
                    "rc-service sshd start && rc-update add sshd",
                    "echo 'root:password' | chpasswd",
                ]
                for cmd in cmds:
                    self.send_cmd(sock, cmd)
                sock.close()
            except Exception as e:
                print(f"Failed {name}: {e}")

if __name__ == "__main__":
    NodeBootstrapper().bootstrap()
