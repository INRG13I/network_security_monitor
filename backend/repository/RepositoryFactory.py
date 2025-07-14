from config.ConfigLoader import ConfigLoader
from backend.repository import (
    LANDeviceJSONRepository, LANDevicePostgresRepository,
    SwitchJSONRepository, SwitchPostgresRepository,
    RouterJSONRepository, RouterPostgresRepository,
    ComputerJSONRepository, ComputerPostgresRepository
)

class RepositoryFactory:
    _config = ConfigLoader()

    @staticmethod
    def get_repository(entity: str, json_path_override: str = None):
        backend = RepositoryFactory._config.backend()
        dsn = RepositoryFactory._config.dsn()

        if backend == "json":
            # If user overrides JSON path, use it; else use default
            json_path = json_path_override or RepositoryFactory._config.json_path(entity)

            match entity.lower():
                case "landevice":
                    return LANDeviceJSONRepository(json_path)
                case "switch":
                    return SwitchJSONRepository(json_path)
                case "router":
                    return RouterJSONRepository(json_path)
                case "computer":
                    return ComputerJSONRepository(json_path)
                case _:
                    raise ValueError(f"Unknown entity: {entity}")

        elif backend == "postgres":
            match entity.lower():
                case "landevice":
                    return LANDevicePostgresRepository(dsn)
                case "switch":
                    return SwitchPostgresRepository(dsn)
                case "router":
                    return RouterPostgresRepository(dsn)
                case "computer":
                    return ComputerPostgresRepository(dsn)
                case _:
                    raise ValueError(f"Unknown entity: {entity}")
        else:
            raise ValueError(f"Unsupported backend: {backend}")
