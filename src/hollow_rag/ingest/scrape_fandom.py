from __future__ import annotations

import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

import html2text
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


@dataclass(frozen=True)
class ScrapeConfig:
    base: str = "https://hollowknight.fandom.com"
    start_url: str = "https://hollowknight.fandom.com/wiki/Special:AllPages"
    rate_limit_seconds: float = 0.5
    cut_offs: tuple[str, ...] = ("##  Gallery", "##  Trivia", "##  References")


def _safe_filename(name: str) -> str:
    name = re.sub(r"[\\/*?:\"<>|]", "_", name)
    return name.strip()


def _get_all_links(cfg: ScrapeConfig) -> list[str]:
    url = cfg.start_url
    links: list[str] = []

    while url:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.select(".mw-allpages-chunk a"):
            href = a.get("href")
            if not href:
                continue
            links.append(cfg.base + str(href))

        next_link = soup.select_one("a.mw-nextlink")
        if next_link:
            href = next_link.get("href")
            url = (cfg.base + str(href)) if href else None
        else:
            url = None

        time.sleep(cfg.rate_limit_seconds)

    return links


def scrape_to_markdown(output_dir: str | Path, *, overwrite: bool = True, cfg: ScrapeConfig | None = None) -> int:
    cfg = cfg or ScrapeConfig()
    output_dir = Path(output_dir)

    if output_dir.exists() and overwrite:
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Collecting all wiki links...")
    all_links = _get_all_links(cfg)
    print(f"Found {len(all_links)} pages")

    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True

    written = 0
    for url in tqdm(all_links):
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            title_node = soup.find("title")
            if not title_node:
                continue

            title = title_node.get_text().replace(" - Hollow Knight Wiki", "")
            filename = _safe_filename(title) + ".md"
            out_path = output_dir / filename

            content = soup.find("div", {"id": "mw-content-text"})
            if not content:
                continue

            md = h.handle(content.prettify())

            with out_path.open("w", encoding="utf-8") as f:
                for line in md.splitlines(True):
                    if line.strip() in cfg.cut_offs:
                        break
                    f.write(line)

            written += 1
        except Exception as e:
            print("Error:", url, e)

    return written
