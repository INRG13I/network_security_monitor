class IsManaged:
    """
    Represents whether a switch is managed or not.
    """

    def __init__(self, value: bool):
        """
        Args:
            value (bool): True if managed.

        Raises:
            ValueError: If value is not boolean.
        """
        if not isinstance(value, bool):
            raise ValueError("is_managed must be a boolean")
        self.value = value

    def __bool__(self):
        return self.value
