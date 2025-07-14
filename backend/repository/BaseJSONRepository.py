import json
from pathlib import Path
from typing import Generic, TypeVar, Type, List, Optional
from backend.domain.Entity import Entity
from backend.repository.EntityRepository import EntityRepository
from backend.validators.DeviceId import DeviceID

T = TypeVar("T", bound=Entity)


class BaseJSONRepository(EntityRepository[T], Generic[T]):
    def __init__(self, filepath: str, entity_cls: Type[T]):
        self.filepath = Path(filepath)
        self.entity_cls = entity_cls
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self._write_data([])

    def _read_data(self) -> List[dict]:
        with self.filepath.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_data(self, data: List[dict]) -> None:
        with self.filepath.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add(self, entity: T) -> None:
        data = self._read_data()
        if any(d["id"] == str(entity.id) for d in data):
            raise ValueError(f"Entity with id {entity.id} already exists.")
        data.append(entity.to_dict())
        self._write_data(data)

    def get(self, entity_id: DeviceID) -> Optional[T]:
        data = self._read_data()
        for d in data:
            if d["id"] == str(entity_id):
                return self.entity_cls.from_dict(d)
        return None

    def update(self, entity: T) -> None:
        data = self._read_data()
        for i, d in enumerate(data):
            if d["id"] == str(entity.id):
                data[i] = entity.to_dict()
                self._write_data(data)
                return
        raise ValueError(f"Entity with id {entity.id} not found.")

    def delete(self, entity_id: DeviceID) -> None:
        data = self._read_data()
        self._write_data([d for d in data if d["id"] != str(entity_id)])

    def list(self) -> List[T]:
        return [self.entity_cls.from_dict(d) for d in self._read_data()]
