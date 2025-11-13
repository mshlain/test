#!/usr/bin/env python3


# Usage
# curl -O https://raw.githubusercontent.com/mshlain/test/refs/heads/main/tool/static.ip.locker.py
# sudo python3 ./static.ip.locker.py


import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

# network:
#   ethernets:
#     ens160:
#       addresses:
#       - 192.168.222.135/24
#       gateway4: 192.168.222.254
#   version: 2

class ToolInfra:
    def __init__(self):
        pass

    def setup_logging(self):
        logger = logging.getLogger("static.ip.locker")

        # console
        formatter = logging.Formatter(
            "%(asctime)s UTC - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # file
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        log_file = f"/var/log/zerto/containers/netplan/{timestamp}.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True, mode=0o755)
        shutil.chown(os.path.dirname(log_file), user="zadmin", group="zadmin")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        os.chmod(log_file, 0o644)

        logger.setLevel(logging.INFO)
        return logger

    def run_cmd(self, cmd, IgnoreReturnCode=False):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            stderr = result.stderr.strip()
            stdout = result.stdout.strip()

            if result.returncode != 0 and not IgnoreReturnCode:
                msg = f"Command '{cmd}' failed with return code {result.returncode}"
                msg += f"\n  STDOUT: {stdout}"
                msg += f"\n  STDERR: {stderr}"
                raise Exception(msg)

            if result.returncode != 0:
                return stderr

            return stderr + "\n" + stdout

        except Exception as e:
            return f"Error: {e}"


class Config:
    def nic_name(self):
        return "ens160"

    def __init__(self):
        pass

class EthernetConfig:
    def __init__(self):
        self.IpAddress = None
        self.SubnetMask = None
        self.Gateway = None
        self.DnsServers = []
    
    def __str__(self):
        dns_str = ", ".join(self.DnsServers) if self.DnsServers else "None"
        return (
            f"EthernetConfig(\n"
            f"  IP Address: {self.IpAddress}\n"
            f"  Subnet Mask: {self.SubnetMask}\n"
            f"  Gateway: {self.Gateway}\n"
            f"  DNS Servers: {dns_str}\n"
            f")"
        )
    
    def validate(self):
        """Validate the ethernet configuration."""
        if not self.IpAddress:
            raise ValueError("IP Address is required")
        if not self.SubnetMask:
            raise ValueError("Subnet Mask is required")
        if not self.Gateway:
            raise ValueError("Gateway is required")
        
        return True

class CurrentEtherentConfigReader:
    def __init__(self, tool_infra: ToolInfra, config: Config):
        self.tool_infra = tool_infra
        self.config = config

    def _read_ip_addr(self, nic: str) -> str:
        ip_output = self.tool_infra.run_cmd(f"ip addr show {nic}", IgnoreReturnCode=True)
        for line in ip_output.split('\n'):
            line = line.strip()
            if line.startswith('inet ') and not line.startswith('inet6'):
                # Format: inet 192.168.111.162/24 brd ...
                parts = line.split()
                if len(parts) >= 2:
                    ip_cidr = parts[1]
                    if '/' in ip_cidr:
                        ip, cidr = ip_cidr.split('/')
                        return ip
                break

        raise Exception("IP address not found")
    
    def _read_subnet_mask(self, nic: str) -> str:
        # Get IP address and subnet mask
        ip_output = self.tool_infra.run_cmd(f"ip addr show {nic}", IgnoreReturnCode=True)
        for line in ip_output.split('\n'):
            line = line.strip()
            if line.startswith('inet ') and not line.startswith('inet6'):
                # Format: inet 192.168.111.162/24 brd ...
                parts = line.split()
                if len(parts) >= 2:
                    ip_cidr = parts[1]
                    if '/' in ip_cidr:
                        ip, cidr = ip_cidr.split('/')
                        return self._cidr_to_netmask(int(cidr))
                break
        raise Exception("Subnet mask not found")
    
    def _read_gateway(self, nic: str) -> str:
        route_output = self.tool_infra.run_cmd(f"ip route show dev {nic}", IgnoreReturnCode=True)
        for line in route_output.split('\n'):
            if 'default via' in line:
                # Format: default via 192.168.111.254 ...
                parts = line.split()
                if 'via' in parts:
                    via_index = parts.index('via')
                    if via_index + 1 < len(parts):
                        return parts[via_index + 1]
                break

        raise Exception("Gateway not found")
    
    def _read_dns_servers(self) -> list:
        result = []
        dns_output = self.tool_infra.run_cmd("cat /etc/resolv.conf", IgnoreReturnCode=True)
        for line in dns_output.split('\n'):
            line = line.strip()
            if line.startswith('nameserver'):
                parts = line.split()
                if len(parts) >= 2:
                    result.append(parts[1])
        return result

    def read(self) -> EthernetConfig:
        eth_cfg = EthernetConfig()
        nic = self.config.nic_name()
        
        # Get IP address and subnet mask
        eth_cfg.IpAddress = self._read_ip_addr(nic)
        eth_cfg.SubnetMask = self._read_subnet_mask(nic)
        eth_cfg.Gateway = self._read_gateway(nic)
        eth_cfg.DnsServers = self._read_dns_servers()

        return eth_cfg
    
    def _cidr_to_netmask(self, cidr: int) -> str:
        """Convert CIDR notation to dotted decimal subnet mask."""
        mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
        return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"

class StaticIpWriter:
    def __init__(self, tool_infra: ToolInfra, config: Config):
        self.tool_infra = tool_infra
        self.config = config

    def write(self, eth_cfg: EthernetConfig):
        """Write static IP configuration to /etc/network/interfaces and apply it."""
        # Validate configuration before writing
        eth_cfg.validate()
        
        nic = self.config.nic_name()
        
        # Backup existing interfaces file
        self._backup_interfaces_file()
        
        # Build interfaces configuration
        interfaces_content = self._build_interfaces_config(nic, eth_cfg)
        
        # Write to /etc/network/interfaces
        interfaces_file = "/etc/network/interfaces"
        
        try:
            with open(interfaces_file, 'w') as f:
                f.write(interfaces_content)
            os.chmod(interfaces_file, 0o644)
            
            # # Write DNS servers to /etc/resolv.conf
            # self._write_dns_config(eth_cfg.DnsServers)
            
            # Restart networking to apply changes
            self._apply_network_config(nic)
            
        except Exception as e:
            # Restore backup on failure
            self._restore_interfaces_backup()
            raise Exception(f"Failed to write network configuration: {e}")
    
    def _build_interfaces_config(self, nic: str, eth_cfg: EthernetConfig) -> str:
        dns_nameservers_value = ' '.join(eth_cfg.DnsServers) if eth_cfg.DnsServers else '8.8.8.8' 

        """Build the content for /etc/network/interfaces file."""
        config = f"""# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
auto {nic}
iface {nic} inet static
    address {eth_cfg.IpAddress}
    netmask {eth_cfg.SubnetMask}
    gateway {eth_cfg.Gateway}
    dns-nameservers {dns_nameservers_value}
"""

        return config
    
    def _write_dns_config(self, dns_servers: list):
        """Write DNS servers to /etc/resolv.conf."""
        if not dns_servers:
            return
        
        # Backup resolv.conf
        resolv_file = "/etc/resolv.conf"
        backup_file = f"{resolv_file}.backup.{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        if os.path.exists(resolv_file):
            shutil.copy2(resolv_file, backup_file)
        
        # Write new resolv.conf
        with open(resolv_file, 'w') as f:
            f.write("# Generated by static.ip.locker.py\n")
            for dns in dns_servers:
                f.write(f"nameserver {dns}\n")
        
        os.chmod(resolv_file, 0o644)
    
    def _apply_network_config(self, nic: str):
        """Apply the network configuration by restarting the interface."""
        # Bring interface down and up to apply new configuration
        self.tool_infra.run_cmd(f"sudo ifdown {nic} && sudo ifup {nic}", IgnoreReturnCode=True)
    
    def _backup_interfaces_file(self):
        """Backup the existing /etc/network/interfaces file."""
        interfaces_file = "/etc/network/interfaces"
        
        if os.path.exists(interfaces_file):
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_file = f"{interfaces_file}.backup.{timestamp}"
            shutil.copy2(interfaces_file, backup_file)
    
    def _restore_interfaces_backup(self):
        """Restore the most recent backup of /etc/network/interfaces."""
        interfaces_file = "/etc/network/interfaces"
        
        # Find most recent backup
        backup_files = [f for f in os.listdir("/etc/network") if f.startswith("interfaces.backup.")]
        
        if backup_files:
            backup_files.sort(reverse=True)
            latest_backup = f"/etc/network/{backup_files[0]}"
            shutil.copy2(latest_backup, interfaces_file)


class App:
    def __init__(self):
        self.tool_infra = ToolInfra()
        self.logger = self.tool_infra.setup_logging()
        self.config = Config()

    def run_impl(self):
        reader = CurrentEtherentConfigReader(self.tool_infra, self.config)
        current_cfg = reader.read()
        print("Current Ethernet Configuration:")
        print(current_cfg)

        writer = StaticIpWriter(self.tool_infra, self.config)
        writer.write(current_cfg)

    def run(self):
        try:
            self.logger.info("")
            self.logger.info("-----------------------------------------")
            self.run_impl()
            self.logger.info("Operation completed successfully.")
            return 0
        except KeyboardInterrupt:
            self.logger.warning("Interrupted by user.")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}", exc_info=e)

        return 1

if __name__ == "__main__":
    # fail_if_no_sudo()
    app = App()
    sys.exit(app.run())

# run with
# sudo python3 ./static.ip.locker.py
