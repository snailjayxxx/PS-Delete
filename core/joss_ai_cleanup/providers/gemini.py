from __future__ import annotations

import base64
from typing import Any

import httpx

from .base import BaseProvider, ProviderError, ProviderResult, find_image_payload, find_image_url, download_image
from ..pipeline import PreparedImage


class GeminiProvider(BaseProvider):
    id = "gemini"
    default_model = "gemini-3.1-flash-image"

    async def edit(
        self,
        prepared: PreparedImage,
        prompt: str,
        model: str | None,
        quality: str,
        options: dict[str, Any],
    ) -> ProviderResult:
        endpoint = str(
            self.settings.get("base_url")
            or "https://generativelanguage.googleapis.com/v1beta/interactions"
        )
        chosen_model = model or self.settings.get("model") or self.default_model
        image_b64 = base64.b64encode(prepared.image_png).decode("ascii")
        mask_b64 = base64.b64encode(prepared.mask_visual_png).decode("ascii")
        image_size = {"low": "1K", "medium": "2K", "high": "4K"}[quality]
        payload = {
            "model": chosen_model,
            "input": [
                {"type": "text", "text": prompt},
                {"type": "image", "data": image_b64, "mime_type": "image/png"},
                {
                    "type": "text",
                    "text": "Mask reference follows. Transparent pixels identify the requested edit area.",
                },
                {"type": "image", "data": mask_b64, "mime_type": "image/png"},
            ],
            "response_format": {
                "type": "image",
                "mime_type": "image/png",
                "image_size": image_size,
            },
        }
        headers = {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
            if response.status_code >= 400:
                raise ProviderError(f"Gemini error {response.status_code}: {response.text[:800]}")
            result = response.json()
            image_bytes = find_image_payload(result)
            if image_bytes is None:
                url = find_image_url(result)
                if url:
                    image_bytes = await download_image(client, url)
        if image_bytes is None:
            raise ProviderError("Gemini response did not contain an image")
        return ProviderResult(
            image_bytes=image_bytes,
            model=str(chosen_model),
            request_id=response.headers.get("x-request-id"),
        )
