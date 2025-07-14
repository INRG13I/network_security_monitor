from backend.repository.BasePostgresRepository import BasePostgresRepository
from backend.domain.Switch import Switch


class SwitchPostgresRepository(BasePostgresRepository[Switch]):
    def __init__(self, dsn: str):
        super().__init__(dsn, Switch, table="switches")
