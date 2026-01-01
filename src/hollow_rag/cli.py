from __future__ import annotations

import argparse
from pathlib import Path

from .paths import get_paths
from .persona import load_persona_text
from .servers.simple_ollama import SimpleOllamaConfig, create_app as create_simple_app, warmup
from .servers.rag_llamaindex import RagServerConfig, create_app as create_rag_app
from .ingest.scrape_fandom import scrape_to_markdown


def _print_server_help(host: str, port: int) -> None:
    base_url = f"http://{host}:{port}" if host not in ("0.0.0.0", "::") else f"http://localhost:{port}"
    print(f"Server: {base_url}")
    print(f"Example: {base_url}/chat?query=Where%20is%20Dirtmouth%3F")


def _knowledge_has_files(knowledge_dir: Path) -> bool:
    if not knowledge_dir.exists() or not knowledge_dir.is_dir():
        return False
    # Cheap check: at least one markdown-ish file
    for p in knowledge_dir.iterdir():
        if p.is_file() and p.suffix.lower() in {".md", ".txt"}:
            return True
    return False


def _add_common_server_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--persona", default=None, help="Path to persona.txt (default: repo root persona.txt)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hollow_rag")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_serve_simple = sub.add_parser("serve-ollama", help="Serve simple persona chat (no RAG)")
    _add_common_server_args(p_serve_simple)
    p_serve_simple.add_argument("--model", default="llama3.2:3b")
    p_serve_simple.add_argument("--max-history", type=int, default=3)

    p_serve_rag = sub.add_parser("serve-rag", help="Serve RAG chat via LlamaIndex")
    _add_common_server_args(p_serve_rag)
    p_serve_rag.add_argument("--model", default="llama3.2:3b")
    p_serve_rag.add_argument("--memory-tokens", type=int, default=1500)

    p_scrape = sub.add_parser("scrape", help="Scrape Hollow Knight fandom wiki into knight_knowledge/")
    p_scrape.add_argument("--out", default=None, help="Output dir (default: repo root knight_knowledge)")
    p_scrape.add_argument("--no-overwrite", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    paths = get_paths()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "scrape":
        out_dir = Path(args.out) if args.out else paths.knowledge_dir
        written = scrape_to_markdown(out_dir, overwrite=not args.no_overwrite)
        print(f"Wrote {written} markdown files to {out_dir}")
        return 0

    persona_path = Path(args.persona) if args.persona else paths.persona_file
    persona_text = load_persona_text(persona_path)

    if args.cmd == "serve-ollama":
        cfg = SimpleOllamaConfig(model_name=args.model, max_history=args.max_history, log_file=str(paths.log_file))
        warmup(system_prompt=persona_text, cfg=cfg)
        app = create_simple_app(system_prompt=persona_text, cfg=cfg)
        _print_server_help(args.host, args.port)
        app.run(args.host, port=args.port)
        return 0

    if args.cmd == "serve-rag":
        if not _knowledge_has_files(paths.knowledge_dir):
            print("Knowledge klasörü boş ya da bulunamadı.")
            print(f"Beklenen konum: {paths.knowledge_dir}")
            print("Önce scrape çalıştır:")
            print("  python main.py scrape")
            print("Sonra tekrar dene:")
            print("  python main.py serve-rag")
            return 2

        cfg = RagServerConfig(model_name=args.model, memory_token_limit=args.memory_tokens)
        app = create_rag_app(
            system_prompt=persona_text,
            knowledge_dir=str(paths.knowledge_dir),
            persist_dir=str(paths.index_dir),
            cfg=cfg,
        )
        if paths.index_dir.exists():
            print(f"Index found: {paths.index_dir} (load)")
        else:
            print(f"Index not found: {paths.index_dir} (will build on first start)")

        print("✧ No cost too great ✧")
        _print_server_help(args.host, args.port)
        app.run(args.host, port=args.port)
        return 0

    raise AssertionError("Unhandled command")
