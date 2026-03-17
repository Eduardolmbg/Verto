"""Módulo de busca web — abstrai a fonte de pesquisa para o resto do sistema."""

from __future__ import annotations

import logging
from datetime import datetime
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from ddgs import DDGS

import config

if TYPE_CHECKING:
    from providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

_BLOCKED_DOMAINS = [
    "investnews.com.br/listas",
    "rankia.com.br",
    "melhoresacoes",
    "sunoresearch.com.br/tudo-sobre",
    "clubedovalor.com.br/lista",
]

_SOURCE_PRIORITY: dict[str, int] = {
    "valor.globo.com": 1,
    "bloomberg.com": 1,
    "reuters.com": 1,
    "infomoney.com.br": 2,
    "exame.com": 2,
    "estadao.com.br": 2,
    "einvestidor.estadao.com.br": 2,
    "moneytimes.com.br": 3,
    "seudinheiro.com": 3,
    "suno.com.br": 3,
}


def _is_quality_source(url: str) -> bool:
    url_lower = url.lower()
    return not any(blocked in url_lower for blocked in _BLOCKED_DOMAINS)


def _source_priority(url: str) -> int:
    url_lower = url.lower()
    for domain, priority in _SOURCE_PRIORITY.items():
        if domain in url_lower:
            return priority
    return 99


def deduplicate_news(news_results: list[dict], similarity_threshold: float = 0.5) -> list[dict]:
    """Remove notícias que cobrem o mesmo evento por similaridade de título/corpo.

    Quando duas notícias são similares, mantém a de fonte com maior prioridade.
    """
    deduplicated: list[dict] = []

    for news in news_results:
        title = news.get("title", "").lower().strip()
        body = news.get("body", "").lower().strip()
        duplicate_of: int | None = None

        for i, existing in enumerate(deduplicated):
            t_sim = SequenceMatcher(None, title, existing.get("title", "").lower()).ratio()
            b_sim = SequenceMatcher(None, body, existing.get("body", "").lower()).ratio()
            if t_sim > similarity_threshold or b_sim > similarity_threshold:
                duplicate_of = i
                break

        if duplicate_of is None:
            deduplicated.append(news)
        else:
            # Substituir se a nova notícia é de fonte melhor
            if _source_priority(news.get("url", "")) < _source_priority(
                deduplicated[duplicate_of].get("url", "")
            ):
                deduplicated[duplicate_of] = news

    return deduplicated


def search_recent_news(ticker: str, company_name: str, max_results: int = 10) -> list[dict]:
    """Busca notícias recentes (último mês) via ddgs.news() com múltiplas queries."""
    queries = [
        f"{ticker} resultados 2025 2026",
        f"{company_name} noticias",
        f"{ticker} dividendos aquisicao guidance",
        f"{ticker} analise recomendacao",
    ]

    all_results: list[dict] = []
    seen_urls: set[str] = set()

    for query in queries:
        for region in ("br-pt", None):
            try:
                with DDGS() as ddgs:
                    raw = list(
                        ddgs.news(
                            query,
                            max_results=5,
                            timelimit="m",
                            **({"region": region} if region else {}),
                        )
                    )
                if raw:
                    break
            except Exception:
                raw = []
                continue

        for r in raw:
            url = r.get("url", "")
            if url and url not in seen_urls and _is_quality_source(url):
                seen_urls.add(url)
                all_results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "url": url,
                    "date": r.get("date", ""),
                    "source": r.get("source", ""),
                })

    all_results.sort(key=lambda x: x.get("date", ""), reverse=True)
    all_results = deduplicate_news(all_results)
    return all_results[:max_results]


def format_news_for_prompt(news_results: list[dict]) -> str:
    """Formata lista de notícias em texto estruturado para o LLM."""
    if not news_results:
        return "Nenhuma noticia encontrada."

    parts: list[str] = []
    for i, n in enumerate(news_results, 1):
        date_str = n.get("date", "")
        try:
            if date_str:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                date_str = dt.strftime("%d/%m/%Y")
        except Exception:
            date_str = date_str[:10] if date_str else "Data N/D"

        parts.append(
            f"[{i}] Data: {date_str} | Fonte: {n.get('source', 'N/D')}\n"
            f"    Titulo: {n.get('title', 'N/D')}\n"
            f"    Resumo: {n.get('body', 'N/D')}\n"
            f"    URL: {n.get('url', 'N/D')}"
        )
    return "\n\n".join(parts)


# ── Busca via DuckDuckGo (fallback universal) ────────────────────────────

def search_duckduckgo(query: str, max_results: int | None = None) -> list[dict]:
    """Busca no DuckDuckGo e retorna lista de resultados.

    Cada resultado é ``{"title": str, "url": str, "snippet": str}``.
    """
    max_results = max_results or config.SEARCH_MAX_RESULTS
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    region="pt-br",
                    max_results=max_results,
                )
            )
        # Se pt-br retornou vazio, tenta sem region
        if not results:
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(query, max_results=max_results)
                )
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            }
            for r in results
        ]
    except Exception:
        logger.exception("Erro na busca DuckDuckGo para: %s", query)
        return []


def format_search_results(results: list[dict]) -> str:
    """Formata resultados de busca em texto legível para o LLM."""
    if not results:
        return "Nenhum resultado encontrado."
    parts: list[str] = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[{i}] {r['title']}\n    URL: {r['url']}\n    {r['snippet']}"
        )
    return "\n\n".join(parts)


# ── Interface unificada ──────────────────────────────────────────────────

def research(
    query: str,
    provider: BaseLLMProvider,
    *,
    synthesis_prompt: str,
    system_prompt: str | None = None,
) -> str:
    """Pesquisa um tema e retorna a síntese gerada pelo LLM.

    Estratégia:
    1. Se o provider suporta search nativo (ex: Gemini), usa direto.
    2. Caso contrário, faz busca via DuckDuckGo + síntese pelo LLM.

    Args:
        query: Termo de busca.
        provider: Instância do LLM provider.
        synthesis_prompt: Prompt para o LLM sintetizar os dados encontrados.
        system_prompt: System prompt opcional.

    Returns:
        Texto sintetizado pelo LLM.
    """
    if provider.supports_search:
        full_prompt = f"{synthesis_prompt}\n\nBusque informações sobre: {query}"
        try:
            text = provider.generate_with_search(
                full_prompt, system_prompt=system_prompt
            )
            if text and text.strip():
                return text
        except Exception:
            logger.warning(
                "Search grounding falhou para '%s', tentando fallback DuckDuckGo",
                query,
            )

    # Fallback: busca DuckDuckGo → contexto → LLM
    results = search_duckduckgo(query)
    context = format_search_results(results)
    full_prompt = (
        f"{synthesis_prompt}\n\n"
        f"Dados encontrados na web:\n\n{context}"
    )
    return provider.generate(full_prompt, system_prompt=system_prompt)
