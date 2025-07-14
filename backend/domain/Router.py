from datetime import timedelta

from backend.domain.LANDevice import LANDevice
from backend.validators.Hostname import Hostname


class Router(LANDevice):
    """
    Represents a router device in the network.
    """

    def __init__(
        self,
        id: str,
        ip: str,
        mac: str,
        vendor: str,
        os: str,
        tags: list,
        ports: list,
        device_status: bool,
        device_uptime: timedelta,
        hostname: str = "Unknown",
        snmp_version: str = None
    ):
        super().__init__(
            id, ip, mac, vendor, os, tags, ports, device_status, device_uptime,
            hostname=hostname, snmp_version=snmp_version
        )
        self.hostname = Hostname(hostname)

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["hostname"] = str(self.hostname)
        return base

    @classmethod
    def from_dict(cls, data: dict) -> "Router":
        return cls(
            id=data["id"],
            ip=data["ip"],
            mac=data["mac"],
            vendor=data["vendor"],
            os=data["os"],
            tags=data.get("tags", []),
            ports=data.get("ports", []),
            device_status=data["device_status"],
            device_uptime=timedelta(seconds=float(data["device_uptime"])),
            hostname=data.get("hostname", "Unknown"),
            snmp_version=data.get("snmp_version")
        )
