from backend.repository.BaseJSONRepository import BaseJSONRepository
from backend.domain.Router import Router


class RouterJSONRepository(BaseJSONRepository[Router]):
    def __init__(self, filepath: str):
        super().__init__(filepath, Router)
