"""Indicadores macroeconomicos do Brasil via API do Banco Central."""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

# ── Mapeamento de indicadores macro por setor/industria ──────────────────

# Indicadores que SEMPRE aparecem (universais)
MACRO_ALWAYS = ["selic", "ipca_12m", "usdbrl"]

# Por setor do yfinance (generico)
MACRO_BY_SECTOR: dict[str, list[str]] = {
    "Energy": ["brent"],
    "Basic Materials": ["brent"],
    "Consumer Defensive": ["igpm"],
    "Consumer Cyclical": ["igpm"],
    "Industrials": ["brent"],
}

# Por industria do yfinance (mais especifico — prioridade sobre setor)
MACRO_BY_INDUSTRY: dict[str, list[str]] = {
    "Oil & Gas E&P": ["brent"],
    "Oil & Gas Integrated": ["brent"],
    "Oil & Gas Refining & Marketing": ["brent"],
    "Oil & Gas Equipment & Services": ["brent"],
    "Steel": [],
    "Other Industrial Metals & Mining": [],
    "Gold": ["gold"],
    "Silver": ["gold"],
    "Agricultural Inputs": ["soybean", "corn"],
    "Farm Products": ["soybean", "corn"],
    "Packaged Foods": ["igpm"],
    "Beverages - Brewers": ["igpm"],
    "Beverages - Non-Alcoholic": ["igpm"],
    "Auto Manufacturers": ["brent"],
    "Airlines": ["brent"],
    "Trucking": ["brent"],
    "Rental & Leasing Services": [],
    "Paper & Paper Products": [],
    "Lumber & Wood Production": [],
    "Staffing & Employment Services": [],
    "Consulting Services": [],
    "Information Technology Services": [],
    "Software - Application": [],
    "Software - Infrastructure": [],
    "Semiconductors": [],
    "Electronic Components": [],
    "Building Products & Equipment": [],
    "Conglomerates": [],
    "Waste Management": [],
    "Specialty Business Services": [],
    "Security & Protection Services": [],
}


def get_relevant_macro_indicators(sector: str, industry: str) -> list[str]:
    """Retorna indicadores macro relevantes para o setor/industria.

    Prioriza industria (mais especifico) sobre setor (mais generico).
    """
    indicators = list(MACRO_ALWAYS)

    # Prioriza industria sobre setor
    industry_extra = MACRO_BY_INDUSTRY.get(industry)
    if industry_extra is not None:
        indicators.extend(industry_extra)
    else:
        sector_extra = MACRO_BY_SECTOR.get(sector, [])
        indicators.extend(sector_extra)

    # Deduplica mantendo ordem
    seen: set[str] = set()
    unique: list[str] = []
    for ind in indicators:
        if ind not in seen:
            seen.add(ind)
            unique.append(ind)
    return unique


# ── Metadata de cada indicador ───────────────────────────────────────────

_MACRO_META: dict[str, tuple[str, str]] = {
    "selic": ("Selic", "percent_raw"),
    "ipca_12m": ("IPCA 12m", "percent_raw"),
    "igpm": ("IGP-M", "percent_raw"),
    "usdbrl": ("USD/BRL", "currency_brl"),
    "brent": ("Brent", "currency_usd"),
    "gold": ("Ouro", "currency_usd"),
    "soybean": ("Soja", "currency_usd_cents"),
    "corn": ("Milho", "currency_usd_cents"),
}


def format_macro_value(fmt: str, value: float) -> str:
    """Formata um valor macro de acordo com seu tipo."""
    if fmt == "percent_raw":
        return f"{value:.2f}%"
    if fmt == "currency_brl":
        return f"R$ {value:.2f}"
    if fmt == "currency_usd":
        return f"US$ {value:.1f}"
    if fmt == "currency_usd_cents":
        return f"US$ {value:.0f}"
    return str(value)


# ── Fetchers individuais ────────────────────────────────────────────────


def _fetch_bcb_series(series_id: int) -> float | None:
    """Busca ultimo valor de uma serie do SGS/BCB."""
    try:
        resp = requests.get(
            f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados/ultimos/1?formato=json",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return float(data[-1]["valor"])
    except Exception:
        logger.debug("SGS serie %s indisponivel", series_id)
    return None


def _fetch_yfinance_price(yf_ticker: str) -> float | None:
    """Busca preco atual de um ticker via yfinance."""
    try:
        import yfinance as yf

        info = yf.Ticker(yf_ticker).info
        price = info.get("regularMarketPrice") or info.get("previousClose")
        if price:
            return float(price)
    except Exception:
        logger.debug("yfinance %s indisponivel", yf_ticker)
    return None


# Mapa: indicador -> funcao que retorna o valor
_FETCHERS: dict[str, Any] = {
    "selic": lambda: _fetch_bcb_series(432),
    "ipca_12m": lambda: _fetch_bcb_series(13522),
    "igpm": lambda: _fetch_bcb_series(189),
    "usdbrl": lambda: _fetch_yfinance_price("BRL=X"),
    "brent": lambda: _fetch_yfinance_price("BZ=F"),
    "gold": lambda: _fetch_yfinance_price("GC=F"),
    "soybean": lambda: _fetch_yfinance_price("ZS=F"),
    "corn": lambda: _fetch_yfinance_price("ZC=F"),
}


# ── Client ───────────────────────────────────────────────────────────────


class MacroClient:
    """Busca indicadores macro do Brasil via BCB e yfinance."""

    def get_macro_context(self, indicators: list[str] | None = None) -> dict:
        """Busca indicadores macro.

        Cada valor retornado: ``{"value": float, "label": str, "format": str}``.
        Se *indicators* for ``None``, busca todos os disponiveis.
        """
        if indicators is None:
            indicators = list(_FETCHERS.keys())

        result: dict = {}
        for ind in indicators:
            fetcher = _FETCHERS.get(ind)
            if not fetcher:
                continue
            val = fetcher()
            if val is not None:
                label, fmt = _MACRO_META.get(ind, (ind, "raw"))
                result[ind] = {"value": val, "label": label, "format": fmt}

        return result
