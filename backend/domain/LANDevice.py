from datetime import timedelta

from backend.domain.Entity import Entity
from backend.validators.DeviceId import DeviceID
from backend.validators.DeviceStatus import DeviceStatus
from backend.validators.DeviceUptime import DeviceUptime
from backend.validators.MACAdress import MACAddress
from backend.validators.PortMapping import PortMapping


class LANDevice(Entity):
    """
    Represents a generic LAN-connected device in the network.
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
        super().__init__(DeviceID(id))
        self.ip = ip
        self.mac = MACAddress(mac)
        self.vendor = vendor
        self.os = os
        self.tags = tags or []
        self.ports = [PortMapping.from_dict(p) for p in ports]
        self.device_status = DeviceStatus(device_status)
        self.device_uptime = DeviceUptime(device_uptime)
        self.hostname = hostname or "Unknown"
        self.snmp_version = snmp_version

    def to_dict(self) -> dict:
        """
        Serializes the LANDevice to a dictionary.
        """
        return {
            "id": str(self.id),
            "ip": self.ip,
            "mac": str(self.mac),
            "vendor": self.vendor,
            "os": self.os,
            "tags": self.tags,
            "ports": [p.to_dict() for p in self.ports],
            "device_status": bool(self.device_status),
            "device_uptime": float(self.device_uptime.uptime.total_seconds()),  # ✅ FIXED HERE
            "hostname": self.hostname,
            "snmp_version": self.snmp_version,
            "type": self.__class__.__name__
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LANDevice":
        """
        Reconstructs a LANDevice from a dictionary.
        """
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
