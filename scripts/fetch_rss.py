"""Fetch real RSS headlines (BBC feeds, no auth) into the articles store.

Usage:
    uv run python scripts/fetch_rss.py
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import httpx
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from trendscout.settings import get_config, resolve_path


def parse_rss(xml_text: str, source: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    rows = []
    for item in root.iter("item"):
        title = item.findtext("title") or ""
        pub = item.findtext("pubDate") or ""
        try:
            published = datetime.strptime(pub[:25].strip(), "%a, %d %b %Y %H:%M:%S")
        except ValueError:
            published = datetime.now()
        if title:
            rows.append({"title": title.strip(), "source": source, "published": published})
    return rows


def main() -> None:
    cfg = get_config()
    rows = []
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        for url in cfg["feeds"]["urls"]:
            source = url.split("/")[2]
            try:
                r = client.get(url)
                r.raise_for_status()
                items = parse_rss(r.text, source)
                rows.extend(items)
                print(f"{url}: {len(items)} items")
            except Exception as exc:
                print(f"{url}: failed ({exc})")
    if not rows:
        raise SystemExit("No items fetched")
    df = pd.DataFrame(rows)
    df["article_id"] = range(1, len(df) + 1)
    df["topic"] = "live"
    out = resolve_path(cfg["data"]["articles_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"Wrote {len(df)} live articles -> {out}")


if __name__ == "__main__":
    main()
