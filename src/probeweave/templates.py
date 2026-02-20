import os

from .common.gns3_utils import get_gns3_connector


def register():
    connector = get_gns3_connector()
    templates = [t['name'] for t in connector.get_templates()]
    if "Alpine-Linux" in templates:
        return

    image_dir = os.path.expanduser("~/GNS3/images/QEMU")
    os.makedirs(image_dir, exist_ok=True)

    # Registration logic...
    template_data = {
        "name": "Alpine-Linux",
        "template_type": "qemu",
        "compute_id": "local",
        "hda_disk_image": "alpine-virt-3.18.4-x86_64.qcow2",
        "ram": 256,
        "qemu_path": "/usr/bin/qemu-system-x86_64"
    }
    connector.http_call("post", f"{connector.base_url}/templates", json_data=template_data)

if __name__ == "__main__":
    register()
