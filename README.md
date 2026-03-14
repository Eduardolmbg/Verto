# thesis-ai 📊

**AI-Powered Stock Research Agent** — Agente de IA que gera relatórios de análise fundamentalista de ações brasileiras automaticamente.

## O que faz

Você digita um ticker de ação brasileira (ex: `WEGE3`, `PETR4`, `VALE3`) e o sistema:

1. 🔍 **Pesquisa** informações sobre a empresa na web (Google Search via Gemini ou DuckDuckGo como fallback)
2. 📊 **Coleta** indicadores financeiros (P/L, EV/EBITDA, ROE, Dividend Yield, etc.)
3. 📰 **Busca** notícias recentes e classifica como positivas, negativas ou neutras
4. 📝 **Gera** um relatório completo de análise fundamentalista em Markdown/HTML

## Arquitetura

```
thesis-ai/
├── app.py                    # Interface Streamlit
├── config.py                 # Configurações e env vars
├── providers/                # Abstração de LLM providers
│   ├── base.py               #   Classe abstrata
│   ├── gemini.py             #   Google Gemini (implementado)
│   ├── openai.py             #   OpenAI GPT (stub)
│   └── groq.py               #   Groq (stub)
├── research/                 # Módulo de pesquisa web
│   ├── web_search.py         #   Busca unificada (Gemini Search / DuckDuckGo)
│   └── data_sources.py       #   Fontes de dados (StatusInvest scraping)
├── agents/                   # Orquestração da análise
│   ├── stock_analyst.py      #   Agente principal (4 etapas)
│   └── prompts.py            #   Prompts organizados
├── reports/                  # Geração de relatórios
│   ├── generator.py          #   Gerador Markdown/HTML
│   └── templates/            #   Templates
├── utils/                    # Helpers
│   └── formatting.py         #   Validação e formatação
└── output/                   # Relatórios gerados
```

### Provider abstrato

O sistema suporta múltiplos LLM providers de forma intercambiável. Atualmente implementado:

| Provider | Status | Search nativo |
|----------|--------|---------------|
| Gemini   | ✅ Implementado | ✅ Google Search grounding |
| OpenAI   | 🔲 Stub | - |
| Groq     | 🔲 Stub | - |

Selecione o provider via variável de ambiente `LLM_PROVIDER` ou pelo dropdown na sidebar do app.

## Como instalar

### Pré-requisitos

- Python 3.10+
- API key do Google Gemini ([obtenha aqui](https://aistudio.google.com/apikey))

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/thesis-ai.git
cd thesis-ai

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env e coloque sua API key
```

## Como rodar

```bash
streamlit run app.py
```

O app abrirá no navegador em `http://localhost:8501`.

### Uso

1. Configure sua API key na sidebar (ou no `.env`)
2. Digite um ticker de ação brasileira (ex: `WEGE3`)
3. Clique em **"Gerar Análise"**
4. Aguarde o agente executar as 4 etapas de pesquisa
5. Baixe o relatório em Markdown ou HTML

## Roadmap

- [x] **Fase 1** — MVP: agente de pesquisa + relatório básico (atual)
- [ ] **Fase 2** — Integração com APIs de dados financeiros (CVM, B3)
- [ ] **Fase 3** — Análise comparativa entre ações do mesmo setor
- [ ] **Fase 4** — Dashboard interativo com gráficos e métricas históricas
- [ ] **Fase 5** — Sistema multi-agente para análises mais profundas

## Disclaimer

⚠️ Os relatórios gerados por este sistema são produzidos por inteligência artificial e **não constituem recomendação de investimento**. Faça sua própria análise antes de investir.

## Licença

MIT
