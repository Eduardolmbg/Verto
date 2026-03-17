"""Catalogo de providers e seus modelos disponiveis."""

from __future__ import annotations

PROVIDER_MODELS: dict[str, dict] = {
    "groq": {
        "name": "Groq",
        "requires_key": True,
        "key_prefix": "gsk_",
        "key_url": "https://console.groq.com/keys",
        "models": {
            "llama-3.3-70b-versatile": {
                "name": "Llama 3.3 70B",
                "description": "Melhor qualidade geral, recomendado",
                "default": True,
            },
            "deepseek-r1-distill-llama-70b": {
                "name": "DeepSeek R1 70B",
                "description": "Forte em raciocinio e analise",
            },
            "meta-llama/llama-4-scout-17b-16e-instruct": {
                "name": "Llama 4 Scout",
                "description": "MoE leve, rapido",
            },
            "llama-3.1-8b-instant": {
                "name": "Llama 3.1 8B",
                "description": "Ultra rapido, menor qualidade",
            },
            "qwen/qwen3-32b": {
                "name": "Qwen 3 32B",
                "description": "Bom para raciocinio e multilingual",
            },
        },
    },
    "gemini": {
        "name": "Google Gemini",
        "requires_key": True,
        "key_prefix": "AI",
        "key_url": "https://aistudio.google.com/apikey",
        "models": {
            "gemini-2.5-flash": {
                "name": "Gemini 2.5 Flash",
                "description": "Rapido e capaz, recomendado",
                "default": True,
            },
            "gemini-2.5-flash-lite": {
                "name": "Gemini 2.5 Flash-Lite",
                "description": "Ultra economico, alto volume",
            },
            "gemini-2.0-flash": {
                "name": "Gemini 2.0 Flash",
                "description": "Versao anterior, estavel",
            },
        },
    },
    "claude": {
        "name": "Anthropic Claude",
        "requires_key": True,
        "key_prefix": "sk-ant-",
        "key_url": "https://console.anthropic.com/settings/keys",
        "models": {
            "claude-sonnet-4-6": {
                "name": "Claude Sonnet 4.6",
                "description": "Melhor custo-beneficio, recomendado",
                "default": True,
            },
            "claude-haiku-4-5-20251001": {
                "name": "Claude Haiku 4.5",
                "description": "Mais rapido e barato",
            },
            "claude-opus-4-6": {
                "name": "Claude Opus 4.6",
                "description": "Mais capaz, mais caro",
            },
        },
    },
    "openai": {
        "name": "OpenAI",
        "requires_key": True,
        "key_prefix": "sk-",
        "key_url": "https://platform.openai.com/api-keys",
        "models": {
            "gpt-4.1": {
                "name": "GPT-4.1",
                "description": "Melhor custo-beneficio, 1M contexto, recomendado",
                "default": True,
            },
            "gpt-4.1-mini": {
                "name": "GPT-4.1 Mini",
                "description": "Rapido e barato",
            },
            "gpt-4.1-nano": {
                "name": "GPT-4.1 Nano",
                "description": "Mais barato, tarefas simples",
            },
            "o3": {
                "name": "o3",
                "description": "Melhor raciocinio, math e codigo",
            },
            "o4-mini": {
                "name": "o4-mini",
                "description": "Raciocinio rapido e economico",
            },
        },
    },
}


def get_default_model(provider: str) -> str:
    """Retorna o model_id padrao de um provider."""
    models = PROVIDER_MODELS.get(provider, {}).get("models", {})
    for model_id, info in models.items():
        if info.get("default"):
            return model_id
    return next(iter(models), "")


def get_model_options(provider: str) -> list[tuple[str, str]]:
    """Retorna lista de (model_id, display_name) para um provider."""
    models = PROVIDER_MODELS.get(provider, {}).get("models", {})
    return [
        (mid, f"{info['name']} — {info['description']}")
        for mid, info in models.items()
    ]


def get_model_display_name(provider: str, model_id: str) -> str:
    """Retorna o nome de exibicao de um modelo especifico."""
    models = PROVIDER_MODELS.get(provider, {}).get("models", {})
    info = models.get(model_id)
    if info:
        return info["name"]
    return model_id
