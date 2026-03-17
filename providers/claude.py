"""Provider Anthropic Claude via SDK oficial."""

from __future__ import annotations

import os

import anthropic

from providers.base import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude via anthropic SDK."""

    name = "claude"

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-6") -> None:
        super().__init__(api_key=api_key or os.getenv("LLM_API_KEY", ""))
        if not self.api_key:
            raise ValueError(
                "API key do Claude nao configurada. "
                "Defina LLM_API_KEY no .env ou passe via sidebar."
            )
        self._client = anthropic.Anthropic(api_key=self.api_key)
        self._model = model

    # ── Core API ─────────────────────────────────────────────────────────

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Chamada padrao de mensagem."""
        kwargs: dict = {
            "model": self._model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)
        return response.content[0].text

    def generate_with_search(
        self, prompt: str, *, system_prompt: str | None = None
    ) -> str:
        """Claude nao suporta search nativo — delega para generate()."""
        return self.generate(prompt, system_prompt=system_prompt)
