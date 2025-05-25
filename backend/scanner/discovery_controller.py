from backend.scanner.arp_scanner import arp_scan
from backend.scanner.nmap_enricher import enrich_with_nmap
from backend.scanner.snmp_enricher import snmp_get_sysdescr
from backend.scanner.tagger import assign_tags, normalize_os_name


def full_discovery_with_choice(ip_range=None):
    print("""
    [+] Choose discovery method:
        1. ARP + Nmap (original method)
        2. ARP + SNMP (SNMPv3 with v2c fallback)
    """)
    choice = input("Enter choice [1/2]: ").strip()

    devices = arp_scan(ip_range)

    if choice == "2":
        for device in devices:
            sysdescr = snmp_get_sysdescr(device['ip'], v3_user='monitor', v3_auth_key='Greenmile132')
            device['os'] = normalize_os_name(sysdescr)
            device = assign_tags(device)
        return devices

    return enrich_with_nmap(devices, timeout=30)


def enrich_device(device, enrich_nmap=True):
    """
    Enrich a single device with Nmap and other methods.
    """
    enriched_device = device.copy()
    if enrich_nmap:
        enriched_device = enrich_with_nmap([enriched_device], None)[0]  # Enrich and return the device
    enriched_device = assign_tags(enriched_device)  # Assign tags after enrichment
    return enriched_device