import ipaddress
import socket
import psutil
import requests


def get_local_ip():
    """Returns the local IP address of the machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

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