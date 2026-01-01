from __future__ import annotations

import os
import sys


def _ensure_src_on_path() -> None:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(repo_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def main() -> int:
    _ensure_src_on_path()
    from hollow_rag.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
