from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


Operation = Literal[
    "remove_object",
    "film_dust",
    "film_scratch",
    "denoise",
    "authorized_overlay",
    "custom",
]


class ProviderConfigUpdate(BaseModel):
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    workspace_id: str | None = None
    endpoint_id: str | None = None
    region: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class RawEditRequest(BaseModel):
    provider: str
    model: str | None = None
    operation: Operation = "remove_object"
    prompt: str = ""
    width: int = Field(gt=0, le=20000)
    height: int = Field(gt=0, le=20000)
    image_rgb_b64: str
    mask_l_b64: str | None = None
    quality: Literal["low", "medium", "high"] = "medium"
    rights_confirmed: bool = False
    provider_options: dict[str, Any] = Field(default_factory=dict)

    @field_validator("prompt")
    @classmethod
    def prompt_length(cls, value: str) -> str:
        if len(value) > 5000:
            raise ValueError("prompt is too long")
        return value.strip()


class RawEditResponse(BaseModel):
    width: int
    height: int
    components: int = 4
    image_rgba_b64: str
    provider: str
    model: str
    request_id: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
