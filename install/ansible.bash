#!/bin/bash

# universal script to install ansible on debian 12 according to official documenation
# at https://docs.ansible.com/ansible/latest/installation_guide/installation_distros.html#installing-ansible-on-debian


# curl -O https://raw.githubusercontent.com/mshlain/test/refs/heads/main/install/ansible.bash && chmod +x ./ansible.bash && sudo ./ansible.bash

# check if ansible already installed
if [ -x "$(command -v ansible)" ]; then
  echo "Ansible is already installed. Installed version:"
  ansible --version
  echo 'To reinstall, first remove installed version with:'
  echo ''
  echo '   > sudo apt remove --purge ansible -yqq && sudo apt autoremove -yqq'
  echo ''
  echo 'and run this script again'
  exit
fi

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit
fi

# check if gpg already installed and install id if not 
if ! [ -x "$(command -v gpg)" ]; then
  apt update
  apt install -y gpg
fi


# Set UBUNTU_CODENAME for Debian 12 (Bookworm)
UBUNTU_CODENAME="jammy"

# Add the Ansible PPA signing key
rm /tmp/ansible-key.asc || true
wget -O /tmp/ansible-key.asc "https://keyserver.ubuntu.com/pks/lookup?fingerprint=on&op=get&search=0x6125E2A8C77F2818FB7BD15B93C4A3FD7BB9C367" 
sudo gpg --dearmour --yes -o /usr/share/keyrings/ansible-archive-keyring.gpg /tmp/ansible-key.asc
rm /tmp/ansible-key.asc || true

# Add the Ansible PPA to apt sources
echo "deb [signed-by=/usr/share/keyrings/ansible-archive-keyring.gpg] http://ppa.launchpad.net/ansible/ansible/ubuntu $UBUNTU_CODENAME main" > /etc/apt/sources.list.d/ansible.list

# Update apt and install Ansible
apt update
apt install -y ansible ansible-lint

# Confirm installation
echo "Ansible installation completed. Installed version:"
ansible --version

# Remove the Ansible PPA from apt sources
rm /etc/apt/sources.list.d/ansible.list

# Remove the Ansible PPA signing key
rm /usr/share/keyrings/ansible-archive-keyring.gpg
