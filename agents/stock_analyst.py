"""Agente de análise fundamentalista — orquestra todas as etapas."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

from agents import prompts
from providers.base import BaseLLMProvider
from research.web_search import research
from research.data_sources import fetch_statusinvest, format_indicators

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Resultado completo de uma análise de ação."""

    ticker: str
    company_name: str = ""
    profile: str = ""
    financials: str = ""
    news: str = ""
    synthesis: str = ""
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return bool(self.profile or self.financials or self.synthesis)


# Tipo para o callback de progresso
ProgressCallback = Callable[[str, float], None]


def _noop_progress(msg: str, pct: float) -> None:
    """Callback padrão que não faz nada."""


class StockAnalyst:
    """Agente que executa a análise fundamentalista passo a passo."""

    def __init__(
        self,
        provider: BaseLLMProvider,
        on_progress: ProgressCallback = _noop_progress,
    ) -> None:
        self.provider = provider
        self.on_progress = on_progress

    def analyze(self, ticker: str) -> AnalysisResult:
        """Executa a análise completa para o ticker informado."""
        ticker = ticker.strip().upper()
        result = AnalysisResult(ticker=ticker)

        # Etapa 1 — Perfil da Empresa
        self.on_progress("Pesquisando perfil da empresa...", 0.0)
        result.profile = self._step_profile(ticker, result)

        # Tenta extrair nome da empresa do perfil para buscas melhores
        result.company_name = self._extract_company_name(ticker, result.profile)

        # Etapa 2 — Dados Financeiros
        self.on_progress("Coletando dados financeiros...", 0.25)
        result.financials = self._step_financials(ticker, result)

        # Etapa 3 — Notícias Recentes
        self.on_progress("Buscando notícias recentes...", 0.50)
        result.news = self._step_news(ticker, result)

        # Etapa 4 — Síntese
        self.on_progress("Gerando síntese de investimento...", 0.75)
        result.synthesis = self._step_synthesis(ticker, result)

        self.on_progress("Análise concluída!", 1.0)
        return result

    # ── Etapas individuais ───────────────────────────────────────────────

    def _step_profile(self, ticker: str, result: AnalysisResult) -> str:
        try:
            query = prompts.PROFILE_SEARCH_QUERY.format(ticker=ticker)
            prompt = prompts.PROFILE_PROMPT.format(ticker=ticker)
            return research(
                query=query,
                provider=self.provider,
                synthesis_prompt=prompt,
                system_prompt=prompts.SYSTEM_PROMPT,
            )
        except Exception as e:
            logger.exception("Erro na etapa de perfil para %s", ticker)
            result.errors["profile"] = str(e)
            return ""

    def _step_financials(self, ticker: str, result: AnalysisResult) -> str:
        try:
            # Tenta enriquecer com dados do StatusInvest
            si_data = fetch_statusinvest(ticker)
            si_text = format_indicators(si_data)

            query = prompts.FINANCIALS_SEARCH_QUERY_1.format(ticker=ticker)
            prompt = prompts.FINANCIALS_PROMPT.format(ticker=ticker)
            if si_text:
                prompt += f"\n\nDados adicionais coletados:\n{si_text}"

            return research(
                query=query,
                provider=self.provider,
                synthesis_prompt=prompt,
                system_prompt=prompts.SYSTEM_PROMPT,
            )
        except Exception as e:
            logger.exception("Erro na etapa financeira para %s", ticker)
            result.errors["financials"] = str(e)
            return ""

    def _step_news(self, ticker: str, result: AnalysisResult) -> str:
        try:
            company = result.company_name or ticker
            query = prompts.NEWS_SEARCH_QUERY.format(
                ticker=ticker, company_name=company
            )
            prompt = prompts.NEWS_PROMPT.format(ticker=ticker)
            return research(
                query=query,
                provider=self.provider,
                synthesis_prompt=prompt,
                system_prompt=prompts.SYSTEM_PROMPT,
            )
        except Exception as e:
            logger.exception("Erro na etapa de notícias para %s", ticker)
            result.errors["news"] = str(e)
            return ""

    def _step_synthesis(self, ticker: str, result: AnalysisResult) -> str:
        try:
            prompt = prompts.SYNTHESIS_PROMPT.format(
                ticker=ticker,
                profile=result.profile or "Não disponível.",
                financials=result.financials or "Não disponível.",
                news=result.news or "Não disponível.",
            )
            # Síntese não precisa de search — usa dados já coletados
            return self.provider.generate(
                prompt, system_prompt=prompts.SYSTEM_PROMPT
            )
        except Exception as e:
            logger.exception("Erro na síntese para %s", ticker)
            result.errors["synthesis"] = str(e)
            return ""

    # ── Helpers ──────────────────────────────────────────────────────────

    def _extract_company_name(self, ticker: str, profile: str) -> str:
        """Tenta extrair o nome da empresa do perfil gerado."""
        if not profile:
            return ticker
        # Pega a primeira linha não-vazia como provável nome
        for line in profile.split("\n"):
            line = line.strip()
            if line and len(line) > 3:
                # Retorna os primeiros ~60 chars da primeira frase
                return line[:60].split(".")[0].strip()
        return ticker
