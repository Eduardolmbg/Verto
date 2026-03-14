"""Stub do provider OpenAI — pronto para implementação futura."""

from __future__ import annotations

from providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT (stub — não implementado ainda)."""

    name = "openai"

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        raise NotImplementedError(
            "Provider 'openai' ainda não implementado. Use 'gemini' como provider."
        )

    def generate_with_search(
        self, prompt: str, *, system_prompt: str | None = None
    ) -> str:
        raise NotImplementedError(
            "Provider 'openai' ainda não implementado. Use 'gemini' como provider."
        )
