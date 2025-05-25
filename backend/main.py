from backend.scanner.discovery_controller import full_discovery_with_choice, enrich_device
from backend.utils.network_utils import get_local_ip, get_netmask_for_ip, get_cidr_from_ip

if __name__ == "__main__":
    local_ip = get_local_ip()
    netmask = get_netmask_for_ip(local_ip)
    cidr = get_cidr_from_ip(local_ip, netmask)

    print(f"\n[+] Local IP: {local_ip}")
    print(f"[+] Subnet Mask: {netmask}")
    print(f"[+] CIDR Block: {cidr}\n")

    # Use the modified discovery function with user choice
    devices = full_discovery_with_choice()

    for dev in devices:
        print(f"IP: {dev['ip']}")
        print(f"  MAC: {dev['mac']}")
        print(f"  Vendor: {dev['vendor']}")
        print(f"  OS: {dev['os']}")
        print(f"  Tags: {', '.join(dev['tags'])}")
        print(f"  Ports: {dev['ports']}")
        print("------")

    # # # If you want to enrich a single device:
    # ip_to_enrich = "192.168.100.104"
    # device_to_enrich = next((dev for dev in devices if dev['ip'] == ip_to_enrich), None)
    # if device_to_enrich:
    #     enriched_device = enrich_device(device_to_enrich)
    #     print(f"Enriched Device: {enriched_device}")
    # else:
    #     print(f"Device with IP {ip_to_enrich} not found in the scan.")