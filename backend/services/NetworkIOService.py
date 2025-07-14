import json
from fastapi import UploadFile
from backend.services.DeviceService import DeviceService

class NetworkIOService:

    @staticmethod
    def export_to_json():
        devices = DeviceService.get_devices()
        return json.dumps(devices, indent=4)

    @staticmethod
    async def import_from_json(file: UploadFile):
        content = await file.read()
        try:
            data = json.loads(content)
            if isinstance(data, list):
                DeviceService.set_devices(data)
                return {"status": "success", "imported": len(data)}
            else:
                return {"status": "error", "message": "Invalid JSON format"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
