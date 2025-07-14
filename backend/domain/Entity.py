from abc import ABC, abstractmethod
from backend.validators.DeviceId import DeviceID


class Entity(ABC):
    """
    Abstract base class for domain entities with a unique identifier.

    Provides identity-based equality and hashing, and enforces that all
    domain entities implement serialization and deserialization methods.
    """

    def __init__(self, id: DeviceID):
        """
        Initialize the Entity with a unique identifier.

        Args:
            id (DeviceID): The unique identifier for the entity.

        Raises:
            ValueError: If the ID is None.
        """
        if id is None:
            raise ValueError("id is required")
        self._id = id

    @property
    def id(self) -> DeviceID:
        """
        Returns the entity's unique identifier.

        Returns:
            DeviceID: The entity's ID.
        """
        return self._id

    def __repr__(self) -> str:
        """
        Returns a string representation of the entity.

        Returns:
            str: Human-readable representation.
        """
        return f"{self.__class__.__name__}(id={self.id!r})"

    def __eq__(self, other) -> bool:
        """
        Compares this entity with another for equality based on ID.

        Args:
            other (Entity): Another entity to compare with.

        Returns:
            bool: True if IDs match, False otherwise.
        """
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Returns a hash value for the entity based on its ID.

        Returns:
            int: The hash of the entity's ID.
        """
        return hash(self.id)

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Serializes the entity to a dictionary.

        Returns:
            dict: A dictionary representing the entity.
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """
        Deserializes an entity from a dictionary.

        Args:
            data (dict): Dictionary containing serialized data.

        Returns:
            Entity: A reconstructed domain entity.
        """
        pass
