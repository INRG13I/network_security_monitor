class ModelName:
    """
    Represents a validated model name of a device.
    """

    def __init__(self, name: str):
        """
        Args:
            name (str): Model name string.

        Raises:
            ValueError: If empty or not a string.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Model name must be a non-empty string")
        self.name = name

    def __str__(self):
        return self.name
