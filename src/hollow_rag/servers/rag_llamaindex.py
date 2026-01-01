from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from flask import Flask, request
from flask_cors import CORS
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.ollama import Ollama

from ..ingest.rag_index import load_or_build_index

if TYPE_CHECKING:
    from llama_index.core.chat_engine.types import ChatMode


@dataclass
class RagServerConfig:
    model_name: str = "llama3.2:3b"
    request_timeout: float = 60.0
    memory_token_limit: int = 1500


def create_app(
    *,
    system_prompt: str,
    knowledge_dir: str,
    persist_dir: str,
    cfg: RagServerConfig,
) -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}})
    app.config["CORS_HEADERS"] = "Content-Type"

    llm = Ollama(model=cfg.model_name, request_timeout=cfg.request_timeout)
    memory = ChatMemoryBuffer.from_defaults(token_limit=cfg.memory_token_limit, llm=llm)

    index = load_or_build_index(
        knowledge_dir=knowledge_dir,
        persist_dir=persist_dir,
        model_name=cfg.model_name,
        request_timeout=cfg.request_timeout,
    )

    chat_engine = index.as_chat_engine(
        chat_mode=cast("ChatMode", "context"),
        llm=llm,
        memory=memory,
        system_prompt=system_prompt,
    )

    @app.get("/")
    def hello_world():
        return "Hollow Knight RAG running..."

    @app.get("/chat")
    def chat():
        query = request.args.get("query", "")
        print("Q:", query)
        response = chat_engine.chat(query)
        print("A:", response)
        return str(response)

    return app
