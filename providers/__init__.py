"""LLM Providers — factory function to get the right provider by name."""

from providers.base import BaseLLMProvider
from providers.gemini import GeminiProvider
from providers.openai import OpenAIProvider
from providers.groq import GroqProvider


_PROVIDERS: dict[str, type[BaseLLMProvider]] = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "groq": GroqProvider,
}


def get_provider(name: str, api_key: str | None = None) -> BaseLLMProvider:
    """Return an instantiated LLM provider.

    Args:
        name: Provider identifier (gemini, openai, groq).
        api_key: API key override. Falls back to env var if not provided.
    """
    name = name.lower().strip()
    if name not in _PROVIDERS:
        available = ", ".join(sorted(_PROVIDERS))
        raise ValueError(f"Provider '{name}' não encontrado. Disponíveis: {available}")
    return _PROVIDERS[name](api_key=api_key)
