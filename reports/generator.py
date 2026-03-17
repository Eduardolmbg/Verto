"""Gerador de relatorios — monta o relatorio final a partir do template."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import config
from agents.stock_analyst import AnalysisResult

_TEMPLATE_PATH = Path(__file__).parent / "templates" / "stock_report.md"


def _load_template() -> str:
    """Carrega o template Markdown do relatorio."""
    return _TEMPLATE_PATH.read_text(encoding="utf-8")


def generate_report(result: AnalysisResult, provider_name: str) -> str:
    """Gera o relatorio Markdown completo a partir dos resultados da analise.

    Args:
        result: Resultado da analise do StockAnalyst.
        provider_name: Nome do provider usado (ex: 'gemini').

    Returns:
        String com o relatorio em Markdown.
    """
    template = _load_template()

    report = template.format(
        company_name=result.company_name or result.ticker,
        ticker=result.ticker,
        date=datetime.now().strftime("%d/%m/%Y %H:%M"),
        provider_name=provider_name,
        profile=result.profile or "_Informacao nao disponivel._",
        financials=result.financials or "_Informacao nao disponivel._",
        news=result.news or "_Informacao nao disponivel._",
        synthesis=result.synthesis or "_Informacao nao disponivel._",
    )

    # Adiciona aviso de erros, se houver
    if result.errors:
        error_lines = ["\n\n---\n\n### Avisos de Processamento\n"]
        for step, err in result.errors.items():
            error_lines.append(f"- **{step}**: {err}")
        report += "\n".join(error_lines)

    return report


def save_report(report: str, ticker: str) -> Path:
    """Salva o relatorio em arquivo na pasta output/.

    Returns:
        Path do arquivo salvo.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ticker}_{timestamp}.md"
    filepath = config.OUTPUT_DIR / filename
    filepath.write_text(report, encoding="utf-8")
    return filepath


def report_to_html(report_md: str) -> str:
    """Converte relatorio Markdown para HTML com tema dark profissional."""
    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="pt-BR">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "<title>Relatorio Verto</title>",
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        "<style>",
        "  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');",
        "  body { font-family: 'DM Sans', sans-serif;",
        "         max-width: 800px; margin: 40px auto; padding: 0 24px;",
        "         line-height: 1.7; color: #e4e4e7; background: #0a0a0f; }",
        "  h1 { color: #e4e4e7; border-bottom: 2px solid #00d4aa;",
        "       padding-bottom: 12px; font-size: 1.6rem; }",
        "  h2 { color: #e4e4e7; margin-top: 36px; font-size: 1.15rem;",
        "       letter-spacing: 0.02em; border-bottom: 1px solid #1e1e2e;",
        "       padding-bottom: 10px; }",
        "  h3 { color: #a1a1aa; font-size: 0.95rem; }",
        "  table { border-collapse: separate; border-spacing: 0;",
        "          width: 100%; margin: 16px 0; border-radius: 8px;",
        "          overflow: hidden; }",
        "  th { background: #1a1a2e; color: #e4e4e7; padding: 12px 16px;",
        "       text-align: left; font-size: 0.85rem; text-transform: uppercase;",
        "       letter-spacing: 0.05em; font-weight: 600;",
        "       border-bottom: 2px solid #00d4aa; }",
        "  td { background: #12121a; color: #e4e4e7; padding: 10px 16px;",
        "       border-bottom: 1px solid #1e1e2e;",
        "       font-family: 'JetBrains Mono', monospace; font-size: 0.88rem; }",
        "  tr:nth-child(even) td { background: rgba(18,18,26,0.7); }",
        "  hr { border: none; border-top: 1px solid #1e1e2e; margin: 32px 0; }",
        "  em { color: #71717a; }",
        "  strong { color: #e4e4e7; }",
        "  li { margin-bottom: 6px; }",
        "  a { color: #00d4aa; }",
        "  .badge { display:inline-block; padding:2px 10px; border-radius:4px;",
        "           font-size:0.75rem; font-weight:700; letter-spacing:0.04em; }",
        "  .badge-positive { background:rgba(16,185,129,0.15); color:#10b981; }",
        "  .badge-negative { background:rgba(239,68,68,0.15); color:#ef4444; }",
        "  .badge-neutral { background:rgba(245,158,11,0.15); color:#f59e0b; }",
        "</style>",
        "</head>",
        "<body>",
        "",
    ]

    # Conversao linha a linha
    in_table = False
    for line in report_md.split("\n"):
        stripped = line.strip()

        if stripped.startswith("# "):
            html_parts.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("## "):
            html_parts.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("### "):
            html_parts.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("---"):
            html_parts.append("<hr>")
        elif stripped.startswith("| ") and "---" not in stripped:
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not in_table:
                in_table = True
                html_parts.append("<table>")
                html_parts.append(
                    "<tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>"
                )
            else:
                html_parts.append(
                    "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
                )
        elif stripped.startswith("|") and "---" in stripped:
            continue
        else:
            if in_table:
                html_parts.append("</table>")
                in_table = False
            if stripped.startswith("- "):
                html_parts.append(f"<li>{stripped[2:]}</li>")
            elif stripped.startswith("*") and stripped.endswith("*"):
                html_parts.append(f"<p><em>{stripped.strip('*')}</em></p>")
            elif stripped:
                html_parts.append(f"<p>{stripped}</p>")
            else:
                html_parts.append("<br>")

    if in_table:
        html_parts.append("</table>")

    html_parts.extend(["", "</body>", "</html>"])
    return "\n".join(html_parts)
