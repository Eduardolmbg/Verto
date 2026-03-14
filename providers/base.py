"""Classe base abstrata para todos os provedores de LLM."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Interface padrão que todo provider de LLM deve implementar."""

    name: str = "base"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or ""

    # ── Core API ─────────────────────────────────────────────────────────

    @abstractmethod
    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Gera texto a partir de um prompt.

        Args:
            prompt: O prompt do usuário.
            system_prompt: Instrução de sistema opcional.

        Returns:
            Texto gerado pelo modelo.
        """

    @abstractmethod
    def generate_with_search(
        self, prompt: str, *, system_prompt: str | None = None
    ) -> str:
        """Gera texto usando busca web integrada (quando disponível).

        Providers que não suportam search nativo devem levantar
        ``NotImplementedError`` ou delegar para ``generate()``.

        Args:
            prompt: O prompt do usuário.
            system_prompt: Instrução de sistema opcional.

        Returns:
            Texto gerado pelo modelo, enriquecido com dados da web.
        """

    # ── Helpers ──────────────────────────────────────────────────────────

    @property
    def supports_search(self) -> bool:
        """Indica se o provider suporta busca web nativa."""
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
