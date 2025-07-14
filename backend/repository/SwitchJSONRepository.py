from backend.repository.BaseJSONRepository import BaseJSONRepository
from backend.domain.Switch import Switch


class SwitchJSONRepository(BaseJSONRepository[Switch]):
    def __init__(self, filepath: str):
        super().__init__(filepath, Switch)
