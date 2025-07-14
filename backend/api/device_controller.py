from fastapi import APIRouter, HTTPException, Query, Request, UploadFile, File, Response

from backend.enrichment.snmp_enricher import snmp_get_status_v3, snmp_get_status_v2c
from backend.services.DeviceService import DeviceService
from backend.services.BandwidthService import BandwidthService
from backend.services.DiscoveryService import DiscoveryService
from backend.utils.network_utils import get_local_ip, get_netmask_for_ip, get_cidr_from_ip
from config.ConfigLoader import ConfigLoader
from backend.services.NetworkIOService import NetworkIOService

router = APIRouter()


@router.get("/devices")
def get_devices():
    return {"devices": DeviceService.get_devices()}


@router.post("/devices/scan")
def scan_devices():
    devices = DiscoveryService.discover_lan_devices()
    DeviceService.set_devices(devices)
    return {"devices": devices}


@router.get("/devices/{ip}/bandwidth")
def get_bandwidth(ip: str, mac: str = Query(...)):
    device = DeviceService.get_cached_device(ip)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    snmp_version = device.get("snmp_version")
    if snmp_version not in ("v2c", "v3"):
        return {"in_kbps": 0.0, "out_kbps": 0.0}

    try:
        return BandwidthService.get_bandwidth(ip, mac, snmp_version=snmp_version)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bandwidth fetch failed: {str(e)}")



@router.post("/devices/enrich/nmap")
def enrich_nmap(ip: str):
    try:
        return DeviceService.enrich_with_nmap(ip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/devices/enrich/snmp")
def enrich_snmp(ip: str):
    try:
        return DeviceService.enrich_with_snmp(ip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/devices/enrich/both")
def enrich_both(ip: str):
    try:
        return DeviceService.enrich_with_both(ip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{ip}/snmp_version", summary="Detect active SNMP version")
def detect_snmp_version(ip: str):
    config = ConfigLoader()
    v3_conf = config.get("snmp_v3", {})
    user = v3_conf.get("username", "admin")
    auth_key = v3_conf.get("auth_key", "admin123")
    auth_protocol = v3_conf.get("auth_protocol", "SHA")

    if snmp_get_status_v3(ip, user, auth_key):
        return {"snmp_version": "v3"}
    elif snmp_get_status_v2c(ip, "public"):
        return {"snmp_version": "v2c"}
    return {"snmp_version": None}

@router.post("/devices/{ip}/change_type")
async def change_device_type(ip: str, request: Request):
    try:
        payload = await request.json()
        new_type = payload.get("new_type")
        if new_type not in ["Router", "Switch", "Computer"]:
            raise HTTPException(status_code=400, detail="Invalid device type")

        device = DeviceService.get_device_by_ip(ip)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        updated = DeviceService.change_device_class(device, new_type)
        return updated
    except Exception as e:
        print(f"[ERROR] Failed to change type: {e}")
        raise HTTPException(status_code=500, detail=f"Type change failed: {str(e)}")


@router.get("/devices/cidr")
def get_cidr():
    ip = get_local_ip()
    netmask = get_netmask_for_ip(ip)
    cidr = get_cidr_from_ip(ip, netmask)
    return {"cidr": cidr}

@router.get("/devices/export")
def export_devices():
    content = NetworkIOService.export_to_json()
    return Response(content=content, media_type="application/json")

@router.post("/devices/import")
async def import_devices(file: UploadFile = File(...)):
    result = await NetworkIOService.import_from_json(file)
    return result