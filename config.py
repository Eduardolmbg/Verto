"""Configurações centrais do thesis-ai."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── LLM Provider ─────────────────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

# ── Gemini defaults ──────────────────────────────────────────────────────
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── Groq defaults ───────────────────────────────────────────────────────
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── Research ─────────────────────────────────────────────────────────────
SEARCH_MAX_RESULTS: int = int(os.getenv("SEARCH_MAX_RESULTS", "8"))
SEARCH_LANGUAGE: str = "pt-br"
SEARCH_REGION: str = "BR"

# ── App metadata ─────────────────────────────────────────────────────────
APP_NAME = "thesis-ai"
APP_TITLE = "thesis-ai"
APP_SUBTITLE = "AI-Powered Equity Research"
APP_VERSION = "0.1.0"
