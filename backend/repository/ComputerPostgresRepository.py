from backend.repository.BasePostgresRepository import BasePostgresRepository
from backend.domain.Computer import Computer


class ComputerPostgresRepository(BasePostgresRepository[Computer]):
    def __init__(self, dsn: str):
        super().__init__(dsn, Computer, table="computers")
