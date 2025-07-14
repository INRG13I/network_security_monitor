class DeviceID:
    """
    Represents a validated unique identifier for a device.

    Attributes:
        value (str): A non-empty string representing the device ID.
    """

    def __init__(self, value: str):
        """
        Initializes a new DeviceID instance.

        Args:
            value (str): The device identifier.

        Raises:
            ValueError: If the value is empty or not a string.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Device ID must be a non-empty string")
        self.value = value

    def __str__(self):
        return self.value
