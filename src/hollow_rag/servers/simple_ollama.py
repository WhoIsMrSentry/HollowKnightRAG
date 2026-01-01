from __future__ import annotations

from dataclasses import dataclass

import ollama
from flask import Flask, request
from flask_cors import CORS

from ..logging_utils import append_log
from ..persona import as_system_message


@dataclass
class SimpleOllamaConfig:
    model_name: str = "llama3.2:3b"
    max_history: int = 3
    log_file: str = "log.txt"


def create_app(*, system_prompt: str, cfg: SimpleOllamaConfig) -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}})
    app.config["CORS_HEADERS"] = "Content-Type"

    system_msg = as_system_message(system_prompt)
    message_history: list[dict] = []

    @app.get("/")
    def hello_world():
        return "Hollow Knight Persona ready..."

    @app.get("/chat")
    def chat():
        nonlocal message_history
        query = request.args.get("query", "")

        append_log(cfg.log_file, "--------------------")
        append_log(cfg.log_file, query)

        prompt: list[dict] = [system_msg, *message_history, {"role": "user", "content": query}]

        response = ollama.chat(model=cfg.model_name, messages=prompt)
        text = str(response["message"]["content"])  # keep UTF-8 (no ASCII stripping)

        append_log(cfg.log_file, text)

        message_history.append({"role": "assistant", "content": text})
        while len(message_history) > cfg.max_history:
            message_history.pop(0)

        return text

    return app


def warmup(*, system_prompt: str, cfg: SimpleOllamaConfig) -> None:
    system_msg = as_system_message(system_prompt)
    response = ollama.chat(
        model=cfg.model_name,
        messages=[system_msg, {"role": "user", "content": 'Reply with "No cost too great"'}],
    )
    print(response["message"]["content"])
