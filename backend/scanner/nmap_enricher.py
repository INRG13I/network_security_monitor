import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import nmap
from backend.scanner.tagger import assign_tags


def enrich_with_nmap(devices, timeout=30, retries=3):
    """
    Uses Nmap to gather OS info and open ports for each device.
    Runs in parallel for each device.

    :param retries: Number of retry attempts for devices that timeout
    """

    def scan_device(device):
        """Scan a single device with Nmap."""
        ip = device['ip']
        scanner = nmap.PortScanner()

        attempt = 0
        while attempt < retries:
            try:
                print(f"[Nmap] Scanning {ip} (Attempt {attempt + 1}/{retries})")

                # Set the Nmap arguments based on the timeout
                if timeout is None:
                    scanner.scan(ip, arguments='-O -Pn -R')
                else:
                    scanner.scan(ip, arguments=f'-O -Pn -R --host-timeout {timeout}s', timeout=timeout)

                if ip in scanner.all_hosts():
                    data = scanner[ip]

                    # OS detection
                    os_matches = data.get('osmatch', [])
                    if os_matches:
                        device['os'] = os_matches[0].get('name', 'Unknown')

                    # Open ports
                    for proto in data.all_protocols():
                        for port in data[proto].keys():
                            device['ports'].append({
                                'port': port,
                                'state': data[proto][port]['state']
                            })

                break  # Exit the loop if the scan is successful
            except nmap.nmap.PortScannerTimeout as e:
                print(f"[Nmap Error] Timeout while scanning {ip}: {e}")
                attempt += 1
                time.sleep(2)  # Wait before retrying
            except Exception as e:
                print(f"[Nmap Error] Could not scan {ip}: {e}")
                break  # Exit the loop if the error is not related to timeout

        # Assign tags after enrichment based on updated OS and ports
        device = assign_tags(device)
        return device

    # Create a thread pool to scan devices in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scan_device, device) for device in devices]
        # Collect results as threads complete
        results = [future.result() for future in as_completed(futures)]

    return results