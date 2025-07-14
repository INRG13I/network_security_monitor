class NumPorts:
    """
    Represents a validated number of ports on a switch.
    """

    def __init__(self, value: int):
        """
        Args:
            value (int): Number of ports.

        Raises:
            ValueError: If not a positive integer.
        """
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Number of ports must be a positive integer")
        self.value = value

    def __int__(self):
        return self.value
