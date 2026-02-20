#!/bin/bash
set -e

echo "Installing GNS3 Dependencies on AlmaLinux 9..."
sudo dnf install -y epel-release
sudo dnf config-manager --set-enabled crb
sudo dnf install -y 
    python3-devel 
    python3-pip 
    gcc 
    elfutils-libelf-devel 
    libpcap-devel 
    cmake 
    git 
    qemu-kvm 
    bridge-utils 
    virt-install 
    libvirt-devel 
    vpcs 
    ubridge 
    telnet

echo "Installing GNS3 Server..."
pip3 install gns3-server

echo "Starting GNS3 Server in background..."
gns3server --daemon

# Wait for it to start
for i in {1..10}; do
    if curl -s http://localhost:3080/v2/version > /dev/null; then
        echo "GNS3 Server is up!"
        exit 0
    fi
    echo "Waiting for GNS3..."
    sleep 2
done

echo "GNS3 failed to start."
exit 1
