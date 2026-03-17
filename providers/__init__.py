"""LLM Providers — factory function to get the right provider by name."""

from providers.base import BaseLLMProvider
from providers.models import PROVIDER_MODELS, get_default_model


def get_provider(
    name: str, api_key: str | None = None, model: str | None = None
) -> BaseLLMProvider:
    """Return an instantiated LLM provider.

    Args:
        name: Provider identifier (gemini, openai, groq, claude).
        api_key: API key override. Falls back to env var if not provided.
        model: Model ID override. Falls back to provider default if not provided.
    """
    name = name.lower().strip()

    if name not in PROVIDER_MODELS:
        available = ", ".join(sorted(PROVIDER_MODELS))
        raise ValueError(f"Provider '{name}' nao encontrado. Disponiveis: {available}")

    if model is None:
        model = get_default_model(name)

    if name == "groq":
        from providers.groq import GroqProvider
        return GroqProvider(api_key=api_key, model=model)

    if name == "gemini":
        from providers.gemini import GeminiProvider
        return GeminiProvider(api_key=api_key, model=model)

    if name == "claude":
        from providers.claude import ClaudeProvider
        return ClaudeProvider(api_key=api_key, model=model)

    if name == "openai":
        from providers.openai_provider import OpenAIProvider
        return OpenAIProvider(api_key=api_key, model=model)

    raise ValueError(f"Provider '{name}' nao implementado.")
