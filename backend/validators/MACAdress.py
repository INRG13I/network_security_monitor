import re


class MACAddress:
    """
    Represents a validated MAC address.

    Attributes:
        mac (str): The MAC address in standard format (e.g., '00:1A:2B:3C:4D:5E').
    """

    def __init__(self, mac: str):
        """
        Initializes a MACAddress instance and validates format.

        Args:
            mac (str): The MAC address string.

        Raises:
            ValueError: If the MAC address format is invalid.
        """
        pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if not re.match(pattern, mac):
            raise ValueError("Invalid MAC address format")
        self.mac = mac

    def __str__(self):
        return self.mac
