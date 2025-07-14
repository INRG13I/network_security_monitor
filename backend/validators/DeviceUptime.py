from datetime import timedelta

class DeviceUptime:
    """
    Represents a validated device uptime duration.

    Attributes:
        uptime (timedelta): The amount of time the device has been running.
    """

    def __init__(self, uptime: timedelta):
        """
        Initializes a DeviceUptime instance.

        Args:
            uptime (timedelta): Duration the device has been online.

        Raises:
            ValueError: If uptime is not a timedelta or is negative.
        """
        if not isinstance(uptime, timedelta) or uptime.total_seconds() < 0:
            raise ValueError("Uptime must be a positive timedelta")
        self.uptime = uptime

    def __str__(self):
        return str(self.uptime)
