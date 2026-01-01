from __future__ import annotations

from pathlib import Path


def load_persona_text(path: str | Path) -> str:
    path = Path(path)
    persona = ""
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if len(line.strip()) > 3 and "#" not in line:
                persona += line
    return persona


def as_system_message(persona_text: str) -> dict:
    return {"role": "system", "content": persona_text}
