class DeviceStatus:
    """
    Represents the boolean status of a device (active/inactive).

    Attributes:
        status (bool): True if the device is active, False otherwise.
    """

    def __init__(self, status: bool):
        """
        Initializes a DeviceStatus instance.

        Args:
            status (bool): The device status.

        Raises:
            ValueError: If the status is not a boolean.
        """
        if not isinstance(status, bool):
            raise ValueError("Status must be a boolean")
        self.status = status

    def __bool__(self):
        return self.status
