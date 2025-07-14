class PortMapping:
    """
    Represents detailed information about a port on a device.

    Attributes:
        port (int): Port number.
        protocol (str): Network protocol, e.g., 'tcp'.
        status (str): Port status, e.g., 'open' or 'closed'.
        service (str): Service name, e.g., 'http'.
        product (str): Product name, e.g., 'nginx'.
        version (str): Product version, e.g., '1.22'.
    """

    def __init__(self, port: int, protocol: str, status: str, service: str = '', product: str = '', version: str = ''):
        if not isinstance(port, int):
            raise ValueError("Port must be an integer")
        if protocol not in ("tcp", "udp"):
            raise ValueError("Protocol must be 'tcp' or 'udp'")
        if status not in ("open", "closed", "filtered"):
            raise ValueError("Status must be 'open', 'closed', or 'filtered'")

        self.port = port
        self.protocol = protocol
        self.status = status
        self.service = service
        self.product = product
        self.version = version

    def to_dict(self):
        return {
            "port": self.port,
            "protocol": self.protocol,
            "status": self.status,
            "service": self.service,
            "product": self.product,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PortMapping":
        return cls(
            port=data["port"],
            protocol=data.get("protocol", "tcp"),
            status=data["status"],
            service=data.get("service", ""),
            product=data.get("product", ""),
            version=data.get("version", "")
        )
