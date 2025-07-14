import time
from backend.enrichment.snmp_enricher import (
    get_in_octets_v2c, get_out_octets_v2c,
    get_in_octets_v3, get_out_octets_v3
)
from backend.utils.network_utils import find_main_interface_index
from config.ConfigLoader import ConfigLoader


class BandwidthService:
    _bandwidth_cache = {}

    @classmethod
    def get_bandwidth(cls, ip, mac, snmp_version="v2c", community="public"):
        try:
            if not snmp_version:
                # Device does not support SNMP
                return {"in_kbps": 0.0, "out_kbps": 0.0}

            if snmp_version == "v3":
                config = ConfigLoader()
                v3 = config.get("snmp_v3", {})
                username = v3.get("username", "admin")
                auth_key = v3.get("auth_key", "admin123")
                auth_protocol = v3.get("auth_protocol", "SHA")

                index = find_main_interface_index(ip, mac, snmp_version="v3", username=username, auth_key=auth_key)
                in_octets = get_in_octets_v3(ip, index, username, auth_key, auth_protocol)
                out_octets = get_out_octets_v3(ip, index, username, auth_key, auth_protocol)

            elif snmp_version == "v2c":
                index = find_main_interface_index(ip, mac, community=community)
                in_octets = get_in_octets_v2c(ip, index, community)
                out_octets = get_out_octets_v2c(ip, index, community)

            else:
                # Unsupported version
                return {"in_kbps": 0.0, "out_kbps": 0.0}

            now = time.time()
            key = f"{ip}-{mac}"
            prev = cls._bandwidth_cache.get(key)

            cls._bandwidth_cache[key] = {
                "time": now,
                "in_octets": in_octets,
                "out_octets": out_octets,
            }

            if not prev:
                return {"in_kbps": 0.0, "out_kbps": 0.0}

            time_diff = now - prev["time"]
            if time_diff <= 0:
                return {"in_kbps": 0.0, "out_kbps": 0.0}

            in_diff = max(0, in_octets - prev["in_octets"])
            out_diff = max(0, out_octets - prev["out_octets"])

            in_kbps = (in_diff * 8) / time_diff / 1000
            out_kbps = (out_diff * 8) / time_diff / 1000

            return {
                "in_kbps": round(in_kbps, 2),
                "out_kbps": round(out_kbps, 2),
            }

        except Exception as e:
            print(f"[Bandwidth Error] {ip}: {e}")
            raise

