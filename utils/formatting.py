"""Helpers de formatação e validação."""

from __future__ import annotations

import re


def validate_ticker(ticker: str) -> tuple[bool, str]:
    """Valida se o ticker parece ser uma ação brasileira válida.

    Returns:
        Tupla (is_valid, message).
    """
    ticker = ticker.strip().upper()
    if not ticker:
        return False, "Digite um ticker."

    # Padrão: 4 letras + 1-2 dígitos (ex: WEGE3, PETR4, BOVA11)
    pattern = r"^[A-Z]{4}\d{1,2}$"
    if not re.match(pattern, ticker):
        return False, (
            f"'{ticker}' não parece ser um ticker válido. "
            "Use o formato: 4 letras + número (ex: WEGE3, PETR4, VALE3)."
        )

    return True, ticker


def truncate(text: str, max_length: int = 500) -> str:
    """Trunca texto mantendo palavras inteiras."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length].rsplit(" ", 1)[0]
    return truncated + "..."
