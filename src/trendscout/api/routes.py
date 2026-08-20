"""API routes: /stories, /trends, /brief, /health (pipeline runs on demand)."""

from __future__ import annotations

import functools
import logging

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from trendscout.brief.write import write_brief
from trendscout.llm.factory import get_provider
from trendscout.settings import get_config, get_settings, resolve_path
from trendscout.stories.cluster import process
from trendscout.trends.burst import detect_bursts

logger = logging.getLogger(__name__)
router = APIRouter()


class BriefRequest(BaseModel):
    provider: str | None = Field(default=None, description="ollama | claude | fake")


@functools.lru_cache(maxsize=1)
def _pipeline():
    path = resolve_path(get_config()["data"]["articles_path"])
    if not path.exists():
        raise FileNotFoundError("No articles; run scripts/make_news.py or scripts/fetch_rss.py")
    articles = pd.read_parquet(path)
    stories, labeled = process(articles)
    return articles, stories, labeled


def invalidate() -> None:
    _pipeline.cache_clear()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "provider": get_settings().llm_provider}


@router.get("/stories")
def stories() -> list[dict]:
    try:
        _, story_list, _ = _pipeline()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return [s.as_dict() for s in sorted(story_list, key=lambda s: -len(s.article_ids))]


@router.get("/trends")
def trends() -> dict:
    try:
        articles, _, labeled = _pipeline()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    dupes = int(labeled["duplicate_of"].notna().sum())
    return {
        "bursts": detect_bursts(articles),
        "n_articles": len(articles),
        "n_near_duplicates": dupes,
    }


@router.post("/brief")
def brief(request: BriefRequest) -> dict:
    try:
        articles, story_list, _ = _pipeline()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    try:
        provider = get_provider(request.provider)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return write_brief(story_list, detect_bursts(articles), provider=provider)
