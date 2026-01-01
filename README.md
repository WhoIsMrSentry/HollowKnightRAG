# HollowKnightRAG

A local-first Retrieval-Augmented Generation (RAG) project for Hollow Knight lore.

This repo provides:
- A scraper to collect Hollow Knight fandom wiki pages into local Markdown (optional)
- A persistent LlamaIndex vector index built from your local knowledge base
- A small Flask HTTP API that answers questions using Ollama
- A persona system prompt (`persona.txt`) tuned for Hollow Knight-style “tablet + dream” responses

## Requirements

- Python 3.10+
- Ollama installed and running
- An Ollama model available (default: `llama3.2:3b`)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Quick start

All commands are run from the repo root.

### Persona-only server (no RAG)

Starts a simple chat server that only uses your `persona.txt` + short message history.

```bash
python main.py serve-ollama
```

### RAG server (retrieval from local knowledge)

Loads `knight_index_storage/` if it exists; otherwise builds an index from `knight_knowledge/`.

```bash
python main.py serve-rag
```

### Scrape wiki content (optional)

Scrapes Hollow Knight fandom wiki pages into `knight_knowledge/` as Markdown.

```bash
python main.py scrape
```

## HTTP API

Both servers expose:

- `GET /chat?query=...`

Example:

`http://localhost:5000/chat?query=Where%20is%20Dirtmouth%3F`

## CLI reference

Show help:

```bash
python main.py --help
python main.py serve-rag --help
```

Common options:

- `--host` (default `0.0.0.0`)
- `--port` (default `5000`)
- `--persona` (path to a persona file; default `persona.txt`)

RAG-specific:

- `serve-rag --model llama3.2:3b --memory-tokens 1500`

Persona-only:

- `serve-ollama --model llama3.2:3b --max-history 3`

Scrape:

- `scrape --out ./knight_knowledge`
- `scrape --no-overwrite`

## Project layout

- `main.py` — main entrypoint (works without installing the package)
- `src/hollow_rag/` — the actual Python package
- `persona.txt` — system prompt / persona instructions
- `knight_knowledge/` — scraped Markdown dataset (generated)
- `knight_index_storage/` — persisted index (generated)
- `3d_models/` — 3D assets included in this repo

## Notes

- `knight_knowledge/` and `knight_index_storage/` are intentionally ignored by git because they can be very large and are generated locally.
- If `serve-rag` says your knowledge directory is missing/empty, run `python main.py scrape` first.

## Optional: editable install

If you prefer `python -m hollow_rag ...`:

```bash
pip install -e .
python -m hollow_rag serve-rag
```