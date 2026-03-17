"""Provider do Google Gemini com suporte a Google Search grounding."""

from __future__ import annotations

import os

from google import genai
from google.genai import types

from providers.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini via google-genai SDK."""

    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash") -> None:
        super().__init__(api_key=api_key or os.getenv("LLM_API_KEY", ""))
        if not self.api_key:
            raise ValueError(
                "API key do Gemini nao configurada. "
                "Defina LLM_API_KEY no .env ou passe via sidebar."
            )
        self._client = genai.Client(api_key=self.api_key)
        self._model = model

    # ── Core API ─────────────────────────────────────────────────────────

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Chamada padrão sem search grounding."""
        contents = self._build_contents(prompt)
        gen_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
        )
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=gen_config,
        )
        return self._extract_text(response)

    def generate_with_search(
        self, prompt: str, *, system_prompt: str | None = None
    ) -> str:
        """Chamada com Google Search grounding habilitado."""
        contents = self._build_contents(prompt)
        search_tool = types.Tool(google_search=types.GoogleSearch())
        gen_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[search_tool],
        )
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=gen_config,
        )
        return self._extract_text(response)

    # ── Helpers ──────────────────────────────────────────────────────────

    @property
    def supports_search(self) -> bool:
        return True

    @staticmethod
    def _extract_text(response) -> str:
        """Extrai texto da resposta, lidando com respostas parciais."""
        # Tenta o atalho .text primeiro
        try:
            if response.text:
                return response.text
        except (ValueError, AttributeError):
            pass

        # Fallback: extrai texto parte a parte dos candidates
        parts_text: list[str] = []
        for candidate in getattr(response, "candidates", []):
            content = getattr(candidate, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []):
                text = getattr(part, "text", None)
                if text:
                    parts_text.append(text)

        return "\n".join(parts_text)

    @staticmethod
    def _build_contents(prompt: str) -> list[types.Content]:
        return [types.Content(role="user", parts=[types.Part(text=prompt)])]
