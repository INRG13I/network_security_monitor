from scapy.layers.l2 import Ether, ARP
from scapy.sendrecv import srp

from backend.scanner.tagger import assign_tags
from backend.utils.network_utils import get_local_ip, get_netmask_for_ip, get_cidr_from_ip, get_vendor


def arp_scan(ip_range=None):
    """Performs ARP scan on the given IP range to discover devices on the network."""
    if ip_range is None:
        local_ip = get_local_ip()
        netmask = get_netmask_for_ip(local_ip)
        ip_range = get_cidr_from_ip(local_ip, netmask)

    print(f"[+] Scanning ARP on {ip_range}")
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    result = srp(packet, timeout=5, verbose=0)[0]

    devices = []
    for _, received in result:
        ip = received.psrc
        mac = received.hwsrc
        device = {
            'ip': ip,
            'mac': mac,
            'vendor': get_vendor(mac),
            'os': 'Unknown',  # Will be enriched later
            'ports': [],  # Will be enriched later
            'tags': []  # Tags will be assigned here
        }
        # Assign tags during ARP scan based on vendor and other known info
        device = assign_tags(device)
        devices.append(device)

    return devices