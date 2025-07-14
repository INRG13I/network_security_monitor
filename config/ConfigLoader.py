import json
from pathlib import Path

class ConfigLoader:
    CONFIG_PATH = Path("config/config.json")

    DEFAULT_CONFIG = {
        "backend": "json",  # or "postgres"
        "json_path_base": "data/",
        "postgres_dsn": "dbname=netdb user=netadmin password=secret host=localhost"
    }

    def __init__(self):
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        if not self.CONFIG_PATH.exists() or self.CONFIG_PATH.stat().st_size == 0:
            self._create_default_config()

        with self.CONFIG_PATH.open("r", encoding="utf-8") as f:
            self._config = json.load(f)

    def _create_default_config(self):
        with self.CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(self.DEFAULT_CONFIG, f, indent=4)
        print(f"✅ Default config created at {self.CONFIG_PATH.resolve()}")

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def backend(self):
        return self._config.get("backend", "json").lower()

    def json_path(self, entity_name: str):
        base = self._config.get("json_path_base", "data/")
        return f"{base}{entity_name.lower()}s.json"

    def dsn(self):
        return self._config.get("postgres_dsn")
