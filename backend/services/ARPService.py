import uuid
from datetime import timedelta

from backend.domain.LANDevice import LANDevice
from backend.enrichment.snmp_enricher import detect_snmp_version


class ARPService:

    @staticmethod
    def create_lan_device_from_arp(ip: str, mac: str) -> LANDevice:
        snmp_version = detect_snmp_version(ip)

        return LANDevice(
            id=str(uuid.uuid4()),
            ip=ip,
            mac=mac,
            vendor="Unknown",
            os="Unknown",
            tags=[],
            ports=[],
            device_status=True,
            device_uptime=timedelta(seconds=0),
            snmp_version=snmp_version,
            hostname="Unknown"
        )

    @staticmethod
    def create_lan_devices_from_arp_scan(scan_results: list[dict]) -> list[LANDevice]:
        """
        Converts a list of ARP scan results (dicts with 'ip' and 'mac') to LANDevice objects.

        Args:
            scan_results (list): list of dicts with 'ip' and 'mac'

        Returns:
            list[LANDevice]: list of LANDevice instances
        """
        devices = []
        for entry in scan_results:
            try:
                device = ARPService.create_lan_device_from_arp(entry['ip'], entry['mac'])
                devices.append(device)
            except Exception as e:
                print(f"[!] Failed to create device for {entry}: {e}")
        return devices
