import ipaddress
import socket
import psutil
import requests
import subprocess
import re
import netifaces

def get_local_ip():
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for link in addrs[netifaces.AF_INET]:
                ip = link.get('addr')
                if ip and not ip.startswith("127."):
                    if ip.startswith("192.168.100."):
                        return ip
    return "Not found"

def get_netmask_for_ip(ip):
    """Finds the netmask for the given local IP by inspecting interfaces."""
    interfaces = psutil.net_if_addrs()
    for addrs in interfaces.values():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip:
                return addr.netmask
    return None

def get_cidr_from_ip(ip, netmask=None):
    """Returns the CIDR block (subnet) of the given IP address and optional netmask."""
    if netmask is None:
        netmask = "255.255.255.0"  # fallback if not provided
    net = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
    return str(net)

def get_vendor(mac):
    """Returns the vendor name from the MAC address using the macvendors API."""
    try:
        r = requests.get(f'https://api.macvendors.com/{mac}', timeout=3)
        if r.status_code == 200:
            return r.text
    except requests.RequestException:
        pass
    return "Unknown"

def run_snmpwalk_v2c(ip: str, oid: str, community: str = 'public') -> list[str]:
    """Run snmpwalk and return a list of output lines."""
    cmd = ['snmpwalk', '-v2c', '-c', community, ip, oid]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"snmpwalk failed: {result.stderr.strip()}")
    return result.stdout.strip().splitlines()

def run_snmpwalk_v3(ip: str, oid: str, username: str, auth_key: str, auth_protocol: str = 'SHA', priv_protocol: str = 'AES') -> list[str]:
    """
    Run snmpwalk using SNMPv3 and return the output lines.

    Default is authNoPriv (authentication only). For full authPriv, expand with privKey, etc.
    """
    cmd = [
        'snmpwalk', '-v3',
        '-u', username,
        '-l', 'authNoPriv',
        '-a', auth_protocol,
        '-A', auth_key,
        ip, oid
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"snmpwalk v3 failed: {result.stderr.strip()}")
    return result.stdout.strip().splitlines()




def run_snmpget_v2c(ip: str, oid: str, community: str = 'public') -> str:
    """Run snmpget and return the extracted value."""
    cmd = ['snmpget', '-v2c', '-c', community, ip, oid]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"snmpget failed: {result.stderr.strip()}")
    line = result.stdout.strip()
    match = re.search(r'=\s+\w+:\s+(.*)', line)
    if not match:
        raise ValueError(f"Unexpected snmpget output: {line}")
    return match.group(1).strip()

def run_snmpget_v3(ip: str, oid: str, username: str, auth_key: str, auth_protocol: str = "SHA") -> str:
    cmd = ['snmpget', '-v3', '-l', 'authNoPriv', '-u', username, '-A', auth_key, '-a', auth_protocol, ip, oid]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"snmpget v3 failed: {result.stderr.strip()}")
    line = result.stdout.strip()
    match = re.search(r'=\s+\w+:\s+(.*)', line)
    if not match:
        raise ValueError(f"Unexpected snmpget v3 output: {line}")
    return match.group(1).strip()


def mac_to_hex(mac: str) -> str:
    """Normalize MAC address to lowercase hex (no delimiters)."""
    return mac.lower().replace(":", "").replace("-", "")


def find_main_interface_index(
    ip: str,
    mac: str,
    community: str = 'public',
    snmp_version: str = 'v2c',
    username: str = None,
    auth_key: str = None
) -> int:
    """
    Find the SNMP interface index matching the MAC address.

    Supports SNMPv2c and SNMPv3 (authNoPriv). Uses `run_snmpwalk_v2c` or `run_snmpwalk_v3`
    based on the `snmp_version` string: 'v2c' or 'v3'.
    """

    mac_target = mac_to_hex(mac)
    oid = '1.3.6.1.2.1.2.2.1.6'  # ifPhysAddress

    if snmp_version == 'v3':
        if not username or not auth_key:
            raise ValueError("SNMPv3 requires username and auth_key")
        lines = run_snmpwalk_v3(ip, oid, username, auth_key)
    elif snmp_version == 'v2c':
        lines = run_snmpwalk_v2c(ip, oid, community)
    else:
        raise ValueError(f"Unsupported SNMP version: {snmp_version}")

    matches = []
    for line in lines:
        m = re.search(r'\.(\d+)\s+=\s+\w+:\s+(.+)', line)
        if not m:
            continue
        index = int(m.group(1))
        raw = m.group(2).strip()

        parts = re.findall(r'[0-9a-fA-F]{1,2}', raw)
        if not parts:
            continue
        hex_mac = ''.join(p.zfill(2) for p in parts).lower()

        if mac_target in hex_mac:
            matches.append((index, hex_mac))

    if not matches:
        raise ValueError(f"MAC {mac} not found on any interface")

    matches.sort(key=lambda x: (x[1] != mac_target, len(x[1])))
    return matches[0][0]


def get_source_ip(dest_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((dest_ip, 161))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip