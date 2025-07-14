import psycopg
import json
from typing import Generic, TypeVar, Type, List, Optional
from backend.domain.Entity import Entity
from backend.repository.EntityRepository import EntityRepository
from backend.validators.DeviceId import DeviceID

T = TypeVar("T", bound=Entity)


class BasePostgresRepository(EntityRepository[T], Generic[T]):
    def __init__(self, dsn: str, entity_cls: Type[T], table: str):
        self.dsn = dsn
        self.entity_cls = entity_cls
        self.table = table

    def _connect(self):
        return psycopg.connect(self.dsn)

    def add(self, entity: T) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self.table} (id, data)
                    VALUES (%s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (str(entity.id), json.dumps(entity.to_dict()))
                )

    def get(self, entity_id: DeviceID) -> Optional[T]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT data FROM {self.table} WHERE id = %s",
                    (str(entity_id),)
                )
                row = cur.fetchone()
                return self.entity_cls.from_dict(row[0]) if row else None

    def update(self, entity: T) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {self.table}
                    SET data = %s
                    WHERE id = %s
                    """,
                    (json.dumps(entity.to_dict()), str(entity.id))
                )

    def delete(self, entity_id: DeviceID) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {self.table} WHERE id = %s", (str(entity_id),))

    def list(self) -> List[T]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT data FROM {self.table}")
                return [self.entity_cls.from_dict(row[0]) for row in cur.fetchall()]
