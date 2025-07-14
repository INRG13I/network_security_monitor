from datetime import timedelta

from backend.domain.LANDevice import LANDevice
from backend.validators.Hostname import Hostname
from backend.validators.CPULoad import CPULoad
from backend.validators.MemoryLoad import MemoryLoad


class Computer(LANDevice):
    """
    Represents a computer.
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
        hostname: str,
        cpu_load: int,
        memory_load: int,
        snmp_version: str = None
    ):
        super().__init__(
            id, ip, mac, vendor, os, tags, ports, device_status, device_uptime,
            hostname=hostname, snmp_version=snmp_version
        )
        self.hostname = Hostname(hostname)
        self.cpu_load = CPULoad(cpu_load)
        self.memory_load = MemoryLoad(memory_load)

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "hostname": str(self.hostname),
            "cpu_load": int(self.cpu_load),
            "memory_load": int(self.memory_load),
        })
        return base

    @classmethod
    def from_dict(cls, data: dict) -> "Computer":
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
            cpu_load=data.get("cpu_load", 0),
            memory_load=data.get("memory_load", 0),
            snmp_version=data.get("snmp_version")
        )
