from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

SERVICE_NAME = "JossAICleanup"
CONFIG_DIR = Path(user_config_dir(SERVICE_NAME, "SnailJOSS"))
CONFIG_FILE = CONFIG_DIR / "providers.json"
FALLBACK_SECRET_FILE = CONFIG_DIR / "secrets.json"


class ConfigStore:
    def __init__(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            return json.loads(path.read_text("utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _write_json(self, path: Path, data: dict[str, Any], secret: bool = False) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
        if secret:
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass

    def get_settings(self, provider: str) -> dict[str, Any]:
        all_settings = self._read_json(CONFIG_FILE)
        value = all_settings.get(provider, {})
        return value if isinstance(value, dict) else {}

    def update_settings(self, provider: str, values: dict[str, Any]) -> dict[str, Any]:
        all_settings = self._read_json(CONFIG_FILE)
        current = all_settings.get(provider, {})
        if not isinstance(current, dict):
            current = {}
        for key, value in values.items():
            if key == "api_key" or value is None:
                continue
            current[key] = value
        all_settings[provider] = current
        self._write_json(CONFIG_FILE, all_settings)
        return current

    def set_api_key(self, provider: str, api_key: str) -> None:
        try:
            import keyring

            keyring.set_password(SERVICE_NAME, provider, api_key)
            return
        except Exception:
            secrets = self._read_json(FALLBACK_SECRET_FILE)
            secrets[provider] = api_key
            self._write_json(FALLBACK_SECRET_FILE, secrets, secret=True)

    def get_api_key(self, provider: str) -> str | None:
        env_name = f"JOSS_{provider.upper().replace('-', '_')}_API_KEY"
        if os.getenv(env_name):
            return os.environ[env_name]
        standard_envs = {
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "dashscope": "DASHSCOPE_API_KEY",
            "volcengine": "ARK_API_KEY",
            "baidu": "QIANFAN_API_KEY",
            "custom-openai": "CUSTOM_OPENAI_API_KEY",
        }
        standard = standard_envs.get(provider)
        if standard and os.getenv(standard):
            return os.environ[standard]
        try:
            import keyring

            value = keyring.get_password(SERVICE_NAME, provider)
            if value:
                return value
        except Exception:
            pass
        value = self._read_json(FALLBACK_SECRET_FILE).get(provider)
        return value if isinstance(value, str) and value else None

    def public_provider_status(self, provider: str) -> dict[str, Any]:
        settings = self.get_settings(provider)
        return {
            "configured": bool(self.get_api_key(provider)),
            "model": settings.get("model"),
            "base_url": settings.get("base_url"),
            "workspace_id": settings.get("workspace_id"),
            "endpoint_id": settings.get("endpoint_id"),
            "region": settings.get("region"),
            "extra": settings.get("extra", {}),
        }
