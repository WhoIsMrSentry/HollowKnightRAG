from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    persona_file: Path
    knowledge_dir: Path
    index_dir: Path
    log_file: Path


def get_project_root() -> Path:
    # src/hollow_rag/paths.py -> src/hollow_rag -> src -> repo root
    return Path(__file__).resolve().parents[2]


def get_paths() -> ProjectPaths:
    root = get_project_root()
    return ProjectPaths(
        root=root,
        persona_file=root / "persona.txt",
        knowledge_dir=root / "knight_knowledge",
        index_dir=root / "knight_index_storage",
        log_file=root / "log.txt",
    )
