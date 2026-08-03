from __future__ import annotations

import base64
from typing import Any

import httpx

from .base import BaseProvider, ProviderError, ProviderResult
from ..pipeline import PreparedImage


class OpenAIProvider(BaseProvider):
    id = "openai"
    default_model = "gpt-image-2"

    async def edit(
        self,
        prepared: PreparedImage,
        prompt: str,
        model: str | None,
        quality: str,
        options: dict[str, Any],
    ) -> ProviderResult:
        base_url = str(self.settings.get("base_url") or "https://api.openai.com/v1").rstrip("/")
        endpoint = f"{base_url}/images/edits"
        chosen_model = model or self.settings.get("model") or self.default_model
        files = {
            "image[]": ("image.png", prepared.image_png, "image/png"),
            "mask": ("mask.png", prepared.mask_png, "image/png"),
        }
        data = {
            "model": chosen_model,
            "prompt": prompt,
            "quality": quality,
            "n": "1",
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, headers=headers, data=data, files=files)
        if response.status_code >= 400:
            raise ProviderError(f"OpenAI error {response.status_code}: {response.text[:800]}")
        payload = response.json()
        try:
            encoded = payload["data"][0]["b64_json"]
            image_bytes = base64.b64decode(encoded)
        except Exception as exc:
            raise ProviderError("OpenAI response did not contain b64_json") from exc
        return ProviderResult(
            image_bytes=image_bytes,
            model=str(chosen_model),
            request_id=response.headers.get("x-request-id"),
        )
