from __future__ import annotations

from pathlib import Path
from datetime import datetime


def append_log(path: str | Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")
