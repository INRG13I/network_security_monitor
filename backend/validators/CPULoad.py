class CPULoad:
    """
    Represents a validated CPU load percentage (0–100).
    """
    def __init__(self, value: int):
        if not isinstance(value, int) or not (0 <= value <= 100):
            raise ValueError("CPU load must be an integer between 0 and 100")
        self.value = value

    def __int__(self):
        return self.value
