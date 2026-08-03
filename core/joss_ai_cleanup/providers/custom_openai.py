from __future__ import annotations

from .openai import OpenAIProvider


class CustomOpenAIProvider(OpenAIProvider):
    id = "custom-openai"
    default_model = "gpt-image-1"
