"""Provider Groq — LPU inference via SDK OpenAI-compatible."""

from __future__ import annotations

import os

from groq import Groq

from providers.base import BaseLLMProvider
import config


class GroqProvider(BaseLLMProvider):
    """Groq LPU via groq SDK."""

    name = "groq"

    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(api_key=api_key or os.getenv("LLM_API_KEY", ""))
        if not self.api_key:
            raise ValueError(
                "API key do Groq nao configurada. "
                "Defina LLM_API_KEY no .env ou passe via sidebar."
            )
        self._client = Groq(api_key=self.api_key)
        self._model = config.GROQ_MODEL

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
        )
        return response.choices[0].message.content or ""

    def generate_with_search(
        self, prompt: str, *, system_prompt: str | None = None
    ) -> str:
        """Groq nao suporta search nativo — delega para generate()."""
        return self.generate(prompt, system_prompt=system_prompt)
