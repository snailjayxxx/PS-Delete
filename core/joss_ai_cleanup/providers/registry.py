from __future__ import annotations

from typing import Any

from .base import BaseProvider, ProviderError
from .baidu import BaiduProvider
from .custom_openai import CustomOpenAIProvider
from .dashscope import DashScopeProvider
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from .volcengine import VolcengineProvider


PROVIDERS: dict[str, type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "dashscope": DashScopeProvider,
    "volcengine": VolcengineProvider,
    "baidu": BaiduProvider,
    "custom-openai": CustomOpenAIProvider,
}


def create_provider(provider_id: str, api_key: str | None, settings: dict[str, Any]) -> BaseProvider:
    cls = PROVIDERS.get(provider_id)
    if cls is None:
        raise ProviderError(f"Unsupported provider: {provider_id}")
    return cls(api_key or "", settings)
