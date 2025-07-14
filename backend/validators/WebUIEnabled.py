class WebUIEnabled:
    """
    Represents whether the switch has a web UI.
    """

    def __init__(self, value: bool):
        """
        Args:
            value (bool): True if web UI is available.

        Raises:
            ValueError: If value is not boolean.
        """
        if not isinstance(value, bool):
            raise ValueError("web_ui must be a boolean")
        self.value = value

    def __bool__(self):
        return self.value
