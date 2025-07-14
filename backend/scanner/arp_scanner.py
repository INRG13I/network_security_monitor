from scapy.layers.l2 import Ether, ARP
from scapy.sendrecv import srp

from backend.utils.network_utils import get_local_ip, get_netmask_for_ip, get_cidr_from_ip


def arp_scan(ip_range=None):
    """Performs ARP scan and returns a list of dicts with 'ip' and 'mac' only."""
    if ip_range is None:
        local_ip = get_local_ip()
        netmask = get_netmask_for_ip(local_ip)
        ip_range = get_cidr_from_ip(local_ip, netmask)

    print(f"[+] Scanning ARP on {ip_range}")
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    result = srp(packet,iface="en6",   timeout=5, verbose=0)[0]

    devices = []
    for _, received in result:
        device = {
            'ip': received.psrc,
            'mac': received.hwsrc
        }
        devices.append(device)

    return devices
