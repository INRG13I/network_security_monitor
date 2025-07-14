from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

from backend.domain.Entity import Entity
from backend.validators.DeviceId import DeviceID

T = TypeVar('T', bound=Entity)

class EntityRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> None:
        pass

    @abstractmethod
    def get(self, entity_id: DeviceID) -> Optional[T]:
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        pass

    @abstractmethod
    def delete(self, entity_id: DeviceID) -> None:
        pass

    @abstractmethod
    def list(self) -> List[T]:
        pass
