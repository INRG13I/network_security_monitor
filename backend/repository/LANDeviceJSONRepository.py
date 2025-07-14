from backend.repository.BaseJSONRepository import BaseJSONRepository
from backend.domain.LANDevice import LANDevice


class LANDeviceJSONRepository(BaseJSONRepository[LANDevice]):
    def __init__(self, filepath: str):
        super().__init__(filepath, LANDevice)
