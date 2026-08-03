from __future__ import annotations

import base64
from typing import Any

import httpx

from .base import BaseProvider, ProviderError, ProviderResult, find_image_payload, find_image_url, download_image
from ..pipeline import PreparedImage


class BaiduProvider(BaseProvider):
    id = "baidu"
    default_model = "qwen-image-edit"

    async def edit(
        self,
        prepared: PreparedImage,
        prompt: str,
        model: str | None,
        quality: str,
        options: dict[str, Any],
    ) -> ProviderResult:
        endpoint = str(self.settings.get("base_url") or "https://qianfan.baidubce.com/v2/images/edits")
        chosen_model = model or self.settings.get("model") or self.default_model
        image_uri = "data:image/png;base64," + base64.b64encode(prepared.image_png).decode("ascii")
        mask_uri = "data:image/png;base64," + base64.b64encode(prepared.mask_visual_png).decode("ascii")
        payload = {
            "model": chosen_model,
            "image": image_uri,
            "prompt": prompt,
            "n": 1,
            "response_format": "b64_json",
        }
        if str(chosen_model).startswith("ernie-irag-edit"):
            payload["mask"] = mask_uri
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
            if response.status_code >= 400:
                raise ProviderError(f"Baidu Qianfan error {response.status_code}: {response.text[:800]}")
            result = response.json()
            image_bytes = find_image_payload(result)
            if image_bytes is None:
                url = find_image_url(result)
                if url:
                    image_bytes = await download_image(client, url)
        if image_bytes is None:
            raise ProviderError("Baidu response did not contain an image")
        return ProviderResult(image_bytes=image_bytes, model=str(chosen_model))
