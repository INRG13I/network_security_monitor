import subprocess
import nmap

scanner = nmap.PortScanner()

def is_device_up_ping(ip):
    cmd = ["ping", "-c", "1", "-W", "1", ip]  # For Linux/macOS
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=2)
        return result.returncode == 0
    except Exception:
        return False

def normalize_nmap_port_data(port_data, port_number, protocol):
    service = port_data.get("name", "") or "unknown"
    product = port_data.get("product", "") or ""
    version = port_data.get("version", "") or ""

    if product.lower() == "tcpwrapped":
        service = "tcpwrapped"
        product = ""

    return {
        "port": port_number,
        "protocol": protocol if protocol in ("tcp", "udp") else "tcp",
        "status": port_data.get("state", "unknown"),
        "service": service,
        "product": product,
        "version": version
    }

def scan_host(ip):
    try:
        scanner.scan(ip, arguments='-sS -sV -O -T4')
        if ip not in scanner.all_hosts():
            return None
        return scanner[ip]
    except Exception as e:
        print(f"[!] Nmap scan error on {ip}: {e}")
        return None

def extract_hostname(scan_result):
    return scan_result.hostname() or "Unknown"

def extract_os(scan_result):
    os_matches = scan_result.get('osmatch', [])
    return os_matches[0]['name'] if os_matches else "Unknown"

def extract_ports(scan_result):
    seen_ports = set()
    ports = []

    for proto in scan_result.all_protocols():
        if proto not in ("tcp", "udp"):
            continue
        for port in scan_result[proto]:
            key = (port, proto)
            if key in seen_ports:
                continue
            seen_ports.add(key)
            port_data = scan_result[proto][port]
            normalized = normalize_nmap_port_data(port_data, port, proto)
            ports.append(normalized)

    return ports

def enrich_device_with_nmap(device):
    ip = device.get('ip')
    device['hostname'] = "Unknown"
    device['os'] = "Unknown"
    device['ports'] = []

    scan_result = scan_host(ip)
    if not scan_result:
        return device

    device['hostname'] = extract_hostname(scan_result)
    device['os'] = extract_os(scan_result)
    device['ports'] = extract_ports(scan_result)

    return device
