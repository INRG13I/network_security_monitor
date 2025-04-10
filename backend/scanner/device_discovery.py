from scapy.layers.l2 import Ether, ARP
from scapy.all import srp
import nmap
import requests
import ipaddress
import os
import sys
import time
import socket

from impacket.nmb import NetBIOS
from zeroconf import ServiceBrowser, Zeroconf, ServiceListener


def require_root():
    if os.name != 'nt':
        if os.geteuid() != 0:
            print("[!] This script must be run as root. Try: sudo python3 ...")
            sys.exit(1)
    else:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("[!] Please run this script as administrator.")
                sys.exit(1)
        except:
            print("[!] Unable to determine admin status. Try running as administrator.")
            sys.exit(1)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def get_cidr_from_ip(ip):
    net = ipaddress.ip_network(ip + "/24", strict=False)
    return str(net)


def get_default_gateway():
    if os.name == "posix":
        try:
            import subprocess
            output = subprocess.check_output("netstat -rn", shell=True).decode()
            for line in output.splitlines():
                if line.startswith("default") or line.startswith("0.0.0.0"):
                    parts = line.split()
                    return parts[1]
        except Exception as e:
            print(f"[!] Failed to get default gateway: {e}")
    return None


def get_vendor(mac):
    try:
        r = requests.get(f'https://api.macvendors.com/{mac}', timeout=3)
        if r.status_code == 429:
            time.sleep(1)
            r = requests.get(f'https://api.macvendors.com/{mac}', timeout=3)
        if r.status_code == 200:
            return r.text
    except requests.RequestException:
        pass
    return "Unknown"


def get_netbios_name(ip):
    try:
        import nmb
        from impacket.nmb import NetBIOS
        n = NetBIOS()
        name = n.getnetbiosname(ip, timeout=2)  # NetBIOS name lookup
        return name.strip() if name else None
    except Exception:
        return None

def resolve_hostname(ip):
    print(f"Resolving hostname for {ip}...")

    # Try DNS resolution first
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        print(f"DNS Hostname: {hostname}")
        return hostname
    except socket.herror:
        print(f"DNS resolution failed for {ip}.")

    # Try NetBIOS resolution (for Windows)
    netbios_name = get_netbios_name(ip)
    if netbios_name:
        print(f"NetBIOS Hostname: {netbios_name}")
        return netbios_name
    else:
        print(f"NetBIOS resolution failed for {ip}.")

    # Try mDNS (for devices using .local name resolution)
    if ip.endswith('.local'):
        mdns_name = ip.split('.')[0]
        print(f"mDNS Hostname: {mdns_name}")
        return mdns_name
    else:
        print(f"mDNS resolution failed for {ip}.")

    return "Hostname not found"





def arp_scan(ip_range=None):
    if ip_range is None:
        local_ip = get_local_ip()
        ip_range = get_cidr_from_ip(local_ip)

    print(f"[+] Scanning ARP on {ip_range}")
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    result = srp(packet, timeout=2, verbose=0)[0]

    devices = []
    for _, received in result:
        ip = received.psrc
        mac = received.hwsrc
        hostname = resolve_hostname(ip)
        vendor = get_vendor(mac)
        devices.append({
            'ip': ip,
            'mac': mac,
            'hostname': hostname,
            'vendor': vendor
        })
    return devices


def enrich_with_nmap(devices):
    scanner = nmap.PortScanner()
    for device in devices:
        ip = device['ip']
        try:
            scanner.scan(ip, arguments='-O -Pn')
            if ip in scanner.all_hosts():
                data = scanner[ip]
                os_matches = data.get('osmatch', [])
                if os_matches:
                    device['os'] = os_matches[0].get('name', 'Unknown')
                else:
                    device['os'] = 'Unknown'

                device['ports'] = []
                for proto in data.all_protocols():
                    for port in data[proto].keys():
                        device['ports'].append({
                            'port': port,
                            'state': data[proto][port]['state']
                        })
        except Exception as e:
            device['os'] = 'Unknown'
            device['ports'] = []
            print(f"[Nmap Error] Could not scan {ip}: {e}")
    return devices


def enrich_with_netbios(devices):
    for device in devices:
        try:
            n = NetBIOS()
            name = n.getnetbiosname(device['ip'], timeout=1)
            if name:
                device['netbios_name'] = name.strip()
        except Exception:
            continue


# mDNS enhancement for discovering .local devices
def discover_mdns():
    zeroconf = Zeroconf()
    services = []

    # Filter for specific mDNS services (e.g., HTTP, SSH, etc.)
    def on_service_state_change(zeroconf, service_type, name, state_change):
        if state_change == Zeroconf.ServiceStateChange.Added:
            try:
                # This filters out only valid service types and checks for well-formed names
                if ".local." in name:
                    services.append(name)
            except Exception as e:
                print(f"[mDNS Error] Failed to add service {name}: {e}")

    # Browsing for specific types like HTTP, SSH, etc.
    service_type = "_http._tcp.local."
    browser = ServiceBrowser(zeroconf, service_type, handlers=[on_service_state_change])

    # Listen for mDNS services for a few seconds
    time.sleep(5)
    zeroconf.close()

    return services


def enrich_with_mdns(devices):
    mdns_services = discover_mdns()
    for device in devices:
        # For devices with matching IP in the mDNS list, append .local to the hostname
        if f"{device['ip']}.local" in mdns_services:
            device['mdns_name'] = f"{device['ip']}.local"


def full_discovery(ip_range=None, enrich=True):
    if ip_range is None:
        local_ip = get_local_ip()
        ip_range = get_cidr_from_ip(local_ip)

    gateway_ip = get_default_gateway()
    devices = arp_scan(ip_range)

    for dev in devices:
        dev['is_router'] = (dev['ip'] == gateway_ip)

    if enrich:
        enrich_with_nmap(devices)
        enrich_with_netbios(devices)
        enrich_with_mdns(devices)

    return devices


if __name__ == "__main__":
    require_root()
    devices = full_discovery(enrich=True)

    for dev in devices:
        label = "[ROUTER]" if dev.get('is_router') else ""
        print(f"IP: {dev['ip']} {label}")
        print(f"  MAC: {dev['mac']}")
        print(f"  Hostname (DNS): {dev.get('hostname', 'N/A')}")
        print(f"  NetBIOS Name: {dev.get('netbios_name', 'N/A')}")
        print(f"  mDNS Name: {dev.get('mdns_name', 'N/A')}")
        print(f"  Vendor: {dev.get('vendor', 'Unknown')}")
        print(f"  OS: {dev.get('os', 'Unknown')}")
        if dev.get('ports'):
            for port in dev['ports']:
                print(f"    Port {port['port']} - {port['state']}")
        print("------")