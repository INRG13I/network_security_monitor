from backend.repository.BasePostgresRepository import BasePostgresRepository
from backend.domain.LANDevice import LANDevice


class LANDevicePostgresRepository(BasePostgresRepository[LANDevice]):
    def __init__(self, dsn: str):
        super().__init__(dsn, LANDevice, table="landevices")
