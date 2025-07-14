from datetime import timedelta

from backend.domain.LANDevice import LANDevice
from backend.validators.ModelName import ModelName
from backend.validators.NumPorts import NumPorts
from backend.validators.WebUIEnabled import WebUIEnabled


class Switch(LANDevice):
    """
    Represents a network switch.
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
        num_ports: int,
        model: str,
        web_ui: bool,
        hostname: str = "Unknown",
        snmp_version: str = None
    ):
        super().__init__(
            id, ip, mac, vendor, os, tags, ports, device_status, device_uptime,
            hostname=hostname, snmp_version=snmp_version
        )
        self.num_ports = NumPorts(num_ports)
        self.model = ModelName(model)
        self.web_ui = WebUIEnabled(web_ui)

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "num_ports": int(self.num_ports),
            "model": str(self.model),
            "web_ui": bool(self.web_ui),
        })
        return base

    @classmethod
    def from_dict(cls, data: dict) -> "Switch":
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
            num_ports=data.get("num_ports", 8),
            model=data.get("model", "Unknown"),
            web_ui=data.get("web_ui", False),
            hostname=data.get("hostname", "Unknown"),
            snmp_version=data.get("snmp_version")
        )
