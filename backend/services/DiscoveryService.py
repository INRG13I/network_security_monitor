import time
from datetime import timedelta

from backend.domain.LANDevice import LANDevice
from backend.domain.Computer import Computer
from backend.domain.Router import Router
from backend.domain.Switch import Switch

from backend.enrichment.snmp_enricher import snmp_get_status_v3, snmp_get_status_v2c
from backend.scanner.arp_scanner import arp_scan
from backend.services.ARPService import ARPService
from backend.services.DeviceService import DeviceService
from config.ConfigLoader import ConfigLoader


class DiscoveryService:
    _last_scan = 0
    _cached_devices = []


    @staticmethod
    def discover_lan_devices():
        now = time.time()
        if now - DiscoveryService._last_scan > 15:
            raw = arp_scan()
            new_scan = ARPService.create_lan_devices_from_arp_scan(raw)

            previous_devices = {d["ip"]: d for d in DeviceService.get_devices()}
            config = ConfigLoader()
            v3 = config.get("snmp_v3", {})
            username = v3.get("username", "admin")
            auth_key = v3.get("auth_key", "admin123")

            updated_devices = []

            for new_dev in new_scan:
                ip = new_dev.ip
                prev_dev = previous_devices.pop(ip, None)

                if snmp_get_status_v3(ip, username, auth_key):
                    new_dev.snmp_version = "v3"
                elif snmp_get_status_v2c(ip, "public"):
                    new_dev.snmp_version = "v2c"
                else:
                    new_dev.snmp_version = None

                if prev_dev:
                    # Reuse ID
                    if "id" in prev_dev:
                        new_dev._id = prev_dev["id"]

                    # Merge enriched fields
                    enriched_fields = ["vendor", "os", "hostname", "tags", "ports", "device_uptime"]
                    new_dict = new_dev.to_dict()
                    for field in enriched_fields:
                        if field in prev_dev and prev_dev[field]:
                            new_dict[field] = prev_dev[field]

                    # Use previous type
                    prev_type = prev_dev.get("type", "LANDevice")
                    promoted_dict = DeviceService.change_device_class(new_dict, prev_type)

                    if prev_type == "Router":
                        promoted_device = Router.from_dict(promoted_dict)
                    elif prev_type == "Switch":
                        promoted_device = Switch.from_dict(promoted_dict)
                    elif prev_type == "Computer":
                        promoted_device = Computer.from_dict(promoted_dict)
                    else:
                        promoted_device = LANDevice.from_dict(promoted_dict)

                    updated_devices.append(promoted_device)
                else:
                    updated_devices.append(new_dev)

            # Add offline devices
            for ip, old_dev in previous_devices.items():
                old_dev["device_status"] = False

                prev_type = old_dev.get("type", "LANDevice")
                if prev_type == "Router":
                    restored = Router.from_dict(old_dev)
                elif prev_type == "Switch":
                    restored = Switch.from_dict(old_dev)
                elif prev_type == "Computer":
                    restored = Computer.from_dict(old_dev)
                else:
                    restored = LANDevice.from_dict(old_dev)

                updated_devices.append(restored)

            DiscoveryService._cached_devices = updated_devices
            DiscoveryService._last_scan = now

        return [d.to_dict() for d in DiscoveryService._cached_devices]
