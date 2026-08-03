from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from ..pipeline import PreparedImage


@dataclass(slots=True)
class ProviderResult:
    image_bytes: bytes
    model: str
    request_id: str | None = None


class ProviderError(RuntimeError):
    pass


class BaseProvider(ABC):
    id: str
    default_model: str

    def __init__(self, api_key: str, settings: dict[str, Any]) -> None:
        if not api_key:
            raise ProviderError(f"Provider {self.id} is not configured")
        self.api_key = api_key
        self.settings = settings
        self.timeout = httpx.Timeout(180.0, connect=30.0)

    @abstractmethod
    async def edit(
        self,
        prepared: PreparedImage,
        prompt: str,
        model: str | None,
        quality: str,
        options: dict[str, Any],
    ) -> ProviderResult:
        raise NotImplementedError


def decode_data_url_or_b64(value: str) -> bytes:
    if value.startswith("data:"):
        _, value = value.split(",", 1)
    return base64.b64decode(value)


def find_image_payload(node: Any) -> bytes | None:
    """Best-effort parser for providers whose response envelope evolves."""
    if isinstance(node, dict):
        mime = str(node.get("mime_type") or node.get("mimeType") or node.get("type") or "")
        for key in ("b64_json", "data", "image_base64", "base64", "image"):
            value = node.get(key)
            if isinstance(value, str) and value:
                if key == "image" and value.startswith("http"):
                    continue
                if "image" in mime.lower() or key in {"b64_json", "image_base64", "base64"}:
                    try:
                        return decode_data_url_or_b64(value)
                    except Exception:
                        pass
        for key in ("output_image", "output", "outputs", "data", "choices", "candidates", "content", "parts", "message"):
            if key in node:
                found = find_image_payload(node[key])
                if found:
                    return found
        for value in node.values():
            found = find_image_payload(value)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_image_payload(item)
            if found:
                return found
    return None


async def download_image(client: httpx.AsyncClient, url: str) -> bytes:
    response = await client.get(url)
    response.raise_for_status()
    return response.content


def find_image_url(node: Any) -> str | None:
    if isinstance(node, dict):
        for key in ("url", "image_url", "output_url"):
            value = node.get(key)
            if isinstance(value, str) and value.startswith("http"):
                return value
        for value in node.values():
            found = find_image_url(value)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_image_url(item)
            if found:
                return found
    return None
