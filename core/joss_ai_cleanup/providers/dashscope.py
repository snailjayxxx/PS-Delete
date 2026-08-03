from __future__ import annotations

import base64
from typing import Any

import httpx

from .base import BaseProvider, ProviderError, ProviderResult, find_image_payload, find_image_url, download_image
from ..pipeline import PreparedImage


class DashScopeProvider(BaseProvider):
    id = "dashscope"
    default_model = "wan2.7-image"

    async def edit(
        self,
        prepared: PreparedImage,
        prompt: str,
        model: str | None,
        quality: str,
        options: dict[str, Any],
    ) -> ProviderResult:
        workspace_id = options.get("workspace_id") or self.settings.get("workspace_id")
        region = options.get("region") or self.settings.get("region") or "cn-beijing"
        if self.settings.get("base_url"):
            endpoint = str(self.settings["base_url"])
        elif not workspace_id:
            raise ProviderError("DashScope requires workspace_id or a custom base_url")
        elif region == "ap-southeast-1":
            endpoint = (
                f"https://{workspace_id}.ap-southeast-1.maas.aliyuncs.com/"
                "api/v1/services/aigc/multimodal-generation/generation"
            )
        else:
            endpoint = (
                f"https://{workspace_id}.cn-beijing.maas.aliyuncs.com/"
                "api/v1/services/aigc/multimodal-generation/generation"
            )
        chosen_model = model or self.settings.get("model") or self.default_model
        image_uri = "data:image/png;base64," + base64.b64encode(prepared.image_png).decode("ascii")
        mask_uri = "data:image/png;base64," + base64.b64encode(prepared.mask_visual_png).decode("ascii")
        size = "1K" if quality == "low" else "2K"
        payload = {
            "model": chosen_model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": image_uri},
                            {"image": mask_uri},
                            {"text": prompt},
                        ],
                    }
                ]
            },
            "parameters": {"size": size, "n": 1, "watermark": False},
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
            if response.status_code >= 400:
                raise ProviderError(f"DashScope error {response.status_code}: {response.text[:800]}")
            result = response.json()
            image_bytes = find_image_payload(result)
            if image_bytes is None:
                url = find_image_url(result)
                if url:
                    image_bytes = await download_image(client, url)
        if image_bytes is None:
            raise ProviderError("DashScope response did not contain an image")
        return ProviderResult(image_bytes=image_bytes, model=str(chosen_model))
