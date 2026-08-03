from __future__ import annotations

import base64

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import ConfigStore
from .pipeline import build_rgba_result, decode_provider_image, prepare_raw_request
from .prompts import build_prompt
from .providers.base import ProviderError
from .providers.registry import PROVIDERS, create_provider
from .schemas import HealthResponse, ProviderConfigUpdate, RawEditRequest, RawEditResponse

store = ConfigStore()
app = FastAPI(title="Joss AI Cleanup Core", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(version=__version__)


@app.get("/v1/providers")
async def list_providers() -> dict[str, object]:
    return {
        "providers": {
            provider_id: {
                "id": provider_id,
                "default_model": provider_cls.default_model,
                **store.public_provider_status(provider_id),
            }
            for provider_id, provider_cls in PROVIDERS.items()
        }
    }


@app.put("/v1/providers/{provider_id}")
async def update_provider(provider_id: str, update: ProviderConfigUpdate) -> dict[str, object]:
    if provider_id not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported provider")
    values = update.model_dump(exclude_none=True)
    api_key = values.pop("api_key", None)
    if api_key:
        store.set_api_key(provider_id, api_key)
    store.update_settings(provider_id, values)
    return {"provider": provider_id, **store.public_provider_status(provider_id)}


@app.post("/v1/edit/raw", response_model=RawEditResponse)
async def edit_raw(request: RawEditRequest) -> RawEditResponse:
    if request.operation == "authorized_overlay" and not request.rights_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Rights confirmation is required for overlay removal",
        )
    try:
        prepared = prepare_raw_request(request)
        settings = store.get_settings(request.provider)
        api_key = store.get_api_key(request.provider)
        provider = create_provider(request.provider, api_key, settings)
        prompt = build_prompt(request.operation, request.prompt, bool(request.mask_l_b64))
        result = await provider.edit(
            prepared=prepared,
            prompt=prompt,
            model=request.model,
            quality=request.quality,
            options=request.provider_options,
        )
        edited = decode_provider_image(result.image_bytes, prepared.image.size)
        rgba = build_rgba_result(prepared.image, edited, prepared.mask)
        return RawEditResponse(
            width=prepared.width,
            height=prepared.height,
            image_rgba_b64=base64.b64encode(rgba).decode("ascii"),
            provider=request.provider,
            model=result.model,
            request_id=result.request_id,
        )
    except (ValueError, ProviderError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
