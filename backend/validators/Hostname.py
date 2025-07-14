class Hostname:
    """
    Represents a validated router hostname.
    """

    def __init__(self, value: str):
        """
        Initialize a Hostname instance.

        Args:
            value (str): The hostname.

        Raises:
            ValueError: If the hostname is empty or invalid.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Hostname must be a non-empty string")
        # Optional: Add format validation for DNS-compliant hostnames
        self.value = value

    def __str__(self):
        return self.value
