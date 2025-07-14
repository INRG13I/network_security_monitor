from backend.repository.BasePostgresRepository import BasePostgresRepository
from backend.domain.Router import Router


class RouterPostgresRepository(BasePostgresRepository[Router]):
    def __init__(self, dsn: str):
        super().__init__(dsn, Router, table="routers")
