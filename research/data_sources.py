"""Fontes de dados específicas para ações brasileiras."""

from __future__ import annotations

import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}


def fetch_statusinvest(ticker: str) -> dict[str, str]:
    """Tenta coletar indicadores básicos do StatusInvest via scraping leve.

    Returns:
        Dicionário com indicadores encontrados ou vazio em caso de erro.
    """
    url = f"https://statusinvest.com.br/acoes/{ticker.lower()}"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        logger.warning("Não foi possível acessar StatusInvest para %s", ticker)
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    indicators: dict[str, str] = {}

    # Tenta extrair os blocos de indicadores
    for item in soup.select("div.info"):
        title_el = item.select_one("h3.title, span.sub-title, span.title")
        value_el = item.select_one("strong.value, span.value")
        if title_el and value_el:
            key = title_el.get_text(strip=True)
            val = value_el.get_text(strip=True)
            if key and val:
                indicators[key] = val

    return indicators


def format_indicators(indicators: dict[str, str]) -> str:
    """Formata dicionário de indicadores em texto legível."""
    if not indicators:
        return ""
    lines = [f"- {k}: {v}" for k, v in indicators.items()]
    return "Indicadores coletados do StatusInvest:\n" + "\n".join(lines)
