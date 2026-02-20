#!/home/sanjayu/shelf/projects/ProbeWeave/.venv/bin/python3
import requests
import os
import sys
from gns3fy import Gns3Connector

def register_templates():
    connector = Gns3Connector(url="http://localhost:3080", user="admin", cred="3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp")
    
    # Check if template already exists
    templates = [t['name'] for t in connector.get_templates()]
    if "Alpine-Linux" in templates:
        print("Template Alpine-Linux already registered.")
        return

    # 1. Download Alpine image if not present
    image_dir = os.path.expanduser("~/GNS3/images/QEMU")
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, "alpine-virt-3.18.4-x86_64.qcow2")
    
    if not os.path.exists(image_path):
        print("Downloading Alpine image...")
        url = "https://downloads.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-virt-3.18.4-x86_64.iso" # Example
        # Note: Usually we use a pre-built qcow2 for faster boot
        # For CI, you might want to host a small qcow2 on your internal artifactory
        r = requests.get(url, allow_redirects=True)
        open(image_path, 'wb').write(r.content)

    # 2. Register template via API
    print("Registering Alpine-Linux template...")
    template_data = {
        "name": "Alpine-Linux",
        "template_type": "qemu",
        "compute_id": "local",
        "hda_disk_image": "alpine-virt-3.18.4-x86_64.qcow2",
        "ram": 256,
        "cpus": 1,
        "qemu_path": "/usr/bin/qemu-system-x86_64",
        "console_type": "telnet",
        "port_name_format": "Ethernet{0}"
    }
    connector.http_call("post", f"{connector.base_url}/templates", json_data=template_data)
    print("Template registered.")

if __name__ == "__main__":
    register_templates()
