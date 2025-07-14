from backend.domain.Computer import Computer
from backend.domain.LANDevice import LANDevice
from backend.domain.Router import Router
from backend.domain.Switch import Switch
from backend.enrichment.nmap_enricher import enrich_device_with_nmap, is_device_up_ping
from backend.enrichment.snmp_enricher import enrich_device_with_snmp
from backend.scanner.tagger import assign_tags
from backend.utils.network_utils import get_vendor


class DeviceService:
    devices_cache = []

    @classmethod
    def get_devices(cls):
        return cls.devices_cache

    @classmethod
    def set_devices(cls, devices):
        cls.devices_cache = devices

    @classmethod
    def get_cached_device(cls, ip: str) -> dict | None:
        return next((d for d in cls.devices_cache if d["ip"] == ip), None)

    @classmethod
    def get_device_by_ip(cls, ip):
        return next((d for d in cls.devices_cache if d["ip"] == ip), None)

    @classmethod
    def update_device(cls, updated_device):
        for idx, dev in enumerate(cls.devices_cache):
            if dev["ip"] == updated_device["ip"]:
                cls.devices_cache[idx] = updated_device
                break

    @classmethod
    def enrich_with_nmap(cls, ip):
        device = cls.get_device_by_ip(ip)
        if not device:
            raise ValueError("Device not found")

        enriched = enrich_device_with_nmap(device)
        enriched["device_status"] = is_device_up_ping(ip)

        if enriched.get("mac"):
            enriched["vendor"] = get_vendor(enriched["mac"])

        assign_tags(enriched)
        cls.update_device(enriched)
        return enriched

    @classmethod
    def enrich_with_snmp(cls, ip):
        device = cls.get_device_by_ip(ip)
        if not device:
            raise ValueError("Device not found")

        enriched = enrich_device_with_snmp(device)

        if enriched.get("mac"):
            enriched["vendor"] = get_vendor(enriched["mac"])

        assign_tags(enriched)
        cls.update_device(enriched)
        return enriched

    @classmethod
    def enrich_with_both(cls, ip):
        device = cls.get_device_by_ip(ip)
        if not device:
            raise ValueError("Device not found")

        device = enrich_device_with_nmap(device)
        device["device_status"] = is_device_up_ping(ip)
        device = enrich_device_with_snmp(device)

        if device.get("mac"):
            device["vendor"] = get_vendor(device["mac"])

        assign_tags(device)
        cls.update_device(device)
        return device

    @classmethod
    def change_device_type(cls, ip: str, new_type: str):
        device = cls.get_device_by_ip(ip)
        if not device:
            raise ValueError("Device not found")

        # Map tags to classes
        type_map = {
            "Router": Router,
            "Switch": Switch,
            "Computer": Computer,
        }

        new_class = type_map.get(new_type)
        if not new_class:
            raise ValueError(f"Unsupported type: {new_type}")

        if isinstance(device, dict):  # Ensure it's a class instance first
            device = LANDevice.from_dict(device)

        # Create new object and update
        promoted = new_class.from_dict(device.to_dict())
        cls.update_device(promoted.to_dict())
        return promoted.to_dict()

    @classmethod
    def change_device_class(cls, device_dict: dict, new_type: str) -> dict:
        from datetime import timedelta

        base_kwargs = {
            "id": device_dict["id"],
            "ip": device_dict["ip"],
            "mac": device_dict["mac"],
            "vendor": device_dict["vendor"],
            "os": device_dict.get("os", ""),
            "tags": device_dict.get("tags", []),
            "ports": device_dict.get("ports", []),
            "device_status": device_dict.get("device_status", False),
            "device_uptime": timedelta(seconds=float(device_dict.get("device_uptime", 0))),
            "hostname": device_dict.get("hostname", "Unknown"),
            "snmp_version": device_dict.get("snmp_version"),
        }

        if new_type == "Router":
            device = Router(**base_kwargs)

        elif new_type == "Switch":
            device = Switch(
                **base_kwargs,
                num_ports=device_dict.get("num_ports", 8),
                model=device_dict.get("model", "Unknown"),
                web_ui=device_dict.get("web_ui", False)
            )

        elif new_type == "Computer":
            device = Computer(
                **base_kwargs,
                cpu_load=device_dict.get("cpu_load", 0),
                memory_load=device_dict.get("memory_load", 0),
            )

        elif new_type == "LANDevice":
            device = LANDevice(**base_kwargs)

        else:
            raise ValueError(f"Unsupported device type: {new_type}")

        cls.update_device(device.to_dict())
        return device.to_dict()
