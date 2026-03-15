# LangChain Python Agent (Weather Example)

Proyecto base en Python que usa LangChain para crear un agente con una tool (`get_weather`) usando Anthropic.

Referencia oficial: https://docs.langchain.com/oss/python/langchain/overview

## Requisitos

- Python 3.10+
- API key de Anthropic

## Instalacion

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuracion

1. Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

2. Completa `ANTHROPIC_API_KEY` en `.env`.

Opcional:
- `LANGCHAIN_MODEL` (por defecto: `claude-sonnet-4-6`)
- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY=...`

## Ejecutar

```bash
python main.py
```

Esto ejecuta el agente con el mensaje:
`what is the weather in sf`
