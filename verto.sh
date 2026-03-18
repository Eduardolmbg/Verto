#!/usr/bin/env bash
set -e

# Detectar comando python (python3 no Linux/Mac, python no Windows/Git Bash)
PYTHON=""
if command -v python3 &>/dev/null && python3 --version &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null && python --version &>/dev/null; then
    PYTHON="python"
fi

# Se ja tem venv e .env, vai direto pro app
if [ -d ".verto" ] && [ -f ".env" ]; then
    # Ativar venv (Windows Git Bash usa Scripts, Linux/Mac usa bin)
    if [ -f ".verto/Scripts/activate" ]; then
        source .verto/Scripts/activate
    else
        source .verto/bin/activate
    fi
    echo "Iniciando Verto..."
    echo "Acesse: http://localhost:8501"
    echo ""
    streamlit run app.py
    exit 0
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║      Verto - Setup Automatico        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Verificar Python
if [ -z "$PYTHON" ]; then
    echo "[ERRO] Python 3 nao encontrado!"
    echo ""
    echo "Instale com:"
    echo "  Windows:       https://www.python.org/downloads/"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  macOS:         brew install python3"
    echo ""
    exit 1
fi

PYVER=$($PYTHON --version 2>&1)
echo "[OK] $PYVER encontrado"
echo ""

# Criar ambiente virtual
if [ ! -d ".verto" ]; then
    echo "[1/3] Criando ambiente virtual..."
    $PYTHON -m venv .verto
    echo "      Ambiente virtual criado."
else
    echo "[1/3] Ambiente virtual ja existe."
fi
echo ""

# Ativar venv
if [ -f ".verto/Scripts/activate" ]; then
    source .verto/Scripts/activate
else
    source .verto/bin/activate
fi

# Instalar dependencias
echo "[2/3] Instalando dependencias..."
pip install -r requirements.txt --quiet
echo "      Dependencias instaladas."
echo ""

# Configurar .env
if [ ! -f ".env" ]; then
    echo "[3/3] Criando arquivo .env..."
    cp .env.example .env
    echo "      Arquivo .env criado."
else
    echo "[3/3] Arquivo .env ja existe."
fi

echo ""
echo "Iniciando Verto..."
echo "Acesse: http://localhost:8501"
echo ""
streamlit run app.py
