"""Indicadores macroeconomicos do Brasil via API do Banco Central."""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


class MacroClient:
    """Busca indicadores macro do Brasil via BCB e yfinance."""

    def get_macro_context(self) -> dict:
        """Busca Selic, IPCA, cambio e Brent. Omite dados indisponiveis."""
        result: dict = {}

        # Selic Meta — SGS serie 432
        try:
            resp = requests.get(
                "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json",
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    result["selic"] = float(data[-1]["valor"])
        except Exception:
            logger.debug("Selic indisponivel")

        # IPCA acumulado 12m — SGS serie 13522
        try:
            resp = requests.get(
                "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/1?formato=json",
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    result["ipca_12m"] = float(data[-1]["valor"])
        except Exception:
            logger.debug("IPCA indisponivel")

        # Cambio USD/BRL
        try:
            import yfinance as yf
            info = yf.Ticker("BRL=X").info
            price = info.get("regularMarketPrice") or info.get("previousClose")
            if price:
                result["usdbrl"] = float(price)
        except Exception:
            logger.debug("USD/BRL indisponivel")

        # Brent (petroleo)
        try:
            import yfinance as yf
            info = yf.Ticker("BZ=F").info
            price = info.get("regularMarketPrice") or info.get("previousClose")
            if price:
                result["brent"] = float(price)
        except Exception:
            logger.debug("Brent indisponivel")

        return result
