from backend.repository.BaseJSONRepository import BaseJSONRepository
from backend.domain.Computer import Computer


class ComputerJSONRepository(BaseJSONRepository[Computer]):
    def __init__(self, filepath: str):
        super().__init__(filepath, Computer)
