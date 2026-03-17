# Verto

**AI-Powered Stock Research Agent** — Agente de IA que gera relatorios de analise fundamentalista de acoes brasileiras (B3) automaticamente.

## O que faz

Voce digita um ticker de acao brasileira (ex: `PETR4`, `VALE3`, `WEGE3`, `BBAS3`) e o sistema:

1. **Coleta dados financeiros** via Yahoo Finance (yfinance) com fallback para brapi.dev
2. **Pesquisa** informacoes sobre a empresa na web (Google Search via Gemini ou DuckDuckGo)
3. **Busca noticias recentes** e classifica como positivas, negativas ou neutras com links para as fontes
4. **Gera grafico interativo** de cotacao historica com seletor de periodo (1M a 5A)
5. **Sintetiza** um relatorio completo de analise fundamentalista com vies de investimento

## Screenshot

Interface dark profissional com tema fintech (Bloomberg-inspired), cards de indicadores financeiros, grafico de cotacao interativo via Plotly, badges de sentimento em noticias e relatorio exportavel em Markdown/HTML.

## Arquitetura

```
Verto/
├── app.py                       # Interface Streamlit (dark theme)
├── config.py                    # Configuracoes, env vars, persistencia .env
├── providers/                   # Abstracao de LLM providers
│   ├── base.py                  #   Classe abstrata BaseLLMProvider
│   ├── gemini.py                #   Google Gemini (com Search grounding)
│   ├── groq.py                  #   Groq (Llama 3.3 70B)
│   └── openai.py                #   OpenAI GPT (stub)
├── research/                    # Modulo de pesquisa e dados
│   ├── yahoo_finance.py         #   Yahoo Finance via yfinance (fonte primaria)
│   ├── brapi.py                 #   brapi.dev API client (fallback)
│   ├── web_search.py            #   Busca web (Gemini Search / DuckDuckGo)
│   └── data_sources.py          #   StatusInvest scraping (legacy)
├── agents/                      # Orquestracao da analise
│   ├── stock_analyst.py         #   Agente principal (5 etapas)
│   └── prompts.py               #   Prompts otimizados para analise
├── reports/                     # Geracao de relatorios
│   ├── generator.py             #   Gerador Markdown/HTML
│   └── templates/               #   Templates de relatorio
├── utils/                       # Helpers
│   ├── theme.py                 #   Dark theme, CSS, SVG icons, componentes visuais
│   └── formatting.py            #   Validacao de ticker, formatacao financeira
└── output/                      # Relatorios gerados
```

## Stack

| Componente | Tecnologia |
|---|---|
| Interface | Streamlit + CSS customizado (dark theme) |
| LLM | Google Gemini / Groq (Llama 3.3) |
| Dados financeiros | Yahoo Finance (yfinance) + brapi.dev (fallback) |
| Graficos | Plotly |
| Busca web | Google Search grounding (Gemini) / DuckDuckGo |
| Icons | SVG inline (Lucide-style) |

## Providers

O sistema suporta multiplos LLM providers de forma intercambiavel:

| Provider | Status | Search nativo | Modelo padrao |
|---|---|---|---|
| Gemini | Implementado | Google Search grounding | gemini-2.5-flash |
| Groq | Implementado | DuckDuckGo (fallback) | llama-3.3-70b-versatile |
| OpenAI | Stub | - | - |

Selecione o provider via variavel de ambiente `LLM_PROVIDER` ou pelo dropdown na sidebar do app.

## Dados financeiros

**Fonte primaria: Yahoo Finance (yfinance)** — gratuito, sem token, sem limite, funciona para qualquer ticker brasileiro.

**Fallback: brapi.dev** — usado quando yfinance falha. O plano gratuito cobre dados basicos; o codigo implementa fallback progressivo em 3 niveis de modulos.

Indicadores coletados incluem: Preco, Market Cap, P/L, EV/EBITDA, ROE, ROA, Margens (EBITDA, Bruta, Operacional, Liquida), Div/Equity, Dividend Yield, Lucro Liquido, Free Cash Flow, Crescimento de Receita/Lucro, entre outros.

## Como instalar

### Pre-requisitos

- Python 3.10+
- API key do Google Gemini ([obtenha aqui](https://aistudio.google.com/apikey)) ou Groq ([obtenha aqui](https://console.groq.com/keys))

### Instalacao

```bash
# Clone o repositorio
git clone https://github.com/seu-usuario/Verto.git
cd Verto

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instale as dependencias
pip install -r requirements.txt

# Configure as variaveis de ambiente
cp .env.example .env
# Edite o .env e coloque sua API key
```

## Como rodar

```bash
streamlit run app.py
```

O app abrira no navegador em `http://localhost:8501`.

### Uso

1. Configure o provider (Gemini ou Groq) e sua API key na sidebar
2. Digite um ticker de acao brasileira (ex: `PETR4`)
3. Clique em **"Gerar Analise"**
4. Aguarde o agente executar as 5 etapas de pesquisa
5. Explore o grafico de cotacao interativo, cards de indicadores e relatorio completo
6. Baixe o relatorio em Markdown ou HTML

### Variaveis de ambiente

| Variavel | Descricao | Padrao |
|---|---|---|
| `LLM_PROVIDER` | Provider de LLM (`gemini`, `groq`) | `gemini` |
| `LLM_API_KEY` | API key do provider selecionado | - |
| `GEMINI_MODEL` | Modelo do Gemini | `gemini-2.5-flash` |
| `GROQ_MODEL` | Modelo do Groq | `llama-3.3-70b-versatile` |
| `BRAPI_TOKEN` | Token brapi.dev (opcional, fallback) | - |
| `SEARCH_MAX_RESULTS` | Max resultados de busca web | `8` |

## Roadmap

- [x] **Fase 1** — MVP: agente de pesquisa + relatorio basico
- [x] **Fase 2** — Integracao Yahoo Finance + brapi.dev com fallback progressivo
- [x] **Fase 3** — Grafico de cotacao interativo com Plotly
- [x] **Fase 4** — Dark theme profissional, cards de indicadores, badges de sentimento
- [ ] **Fase 5** — Analise comparativa entre acoes do mesmo setor
- [ ] **Fase 6** — Sistema multi-agente para analises mais profundas

## Licenca

MIT
