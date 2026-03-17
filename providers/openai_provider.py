"""Provider OpenAI GPT via SDK oficial."""

from __future__ import annotations

import os

from openai import OpenAI

from providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT via openai SDK."""

    name = "openai"

    def __init__(self, api_key: str | None = None, model: str = "gpt-4.1") -> None:
        super().__init__(api_key=api_key or os.getenv("LLM_API_KEY", ""))
        if not self.api_key:
            raise ValueError(
                "API key da OpenAI nao configurada. "
                "Defina LLM_API_KEY no .env ou passe via sidebar."
            )
        self._client = OpenAI(api_key=self.api_key)
        self._model = model

    # ── Core API ─────────────────────────────────────────────────────────

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Chamada padrao de chat completion."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.3,
            max_tokens=4096,
        )
        return response.choices[0].message.content or ""

    def generate_with_search(
        self, prompt: str, *, system_prompt: str | None = None
    ) -> str:
        """OpenAI nao suporta search nativo gratuito — delega para generate()."""
        return self.generate(prompt, system_prompt=system_prompt)
