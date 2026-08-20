"""Daily-brief agent: top stories -> a cited executive brief."""

from __future__ import annotations

from trendscout.llm.base import LLMProvider
from trendscout.llm.factory import get_provider
from trendscout.settings import get_config
from trendscout.stories.cluster import Story

SYSTEM = (
    "You write terse executive news briefs. Use only the provided stories; cite each "
    "item as [source-count sources]. Lead with bursts. Never invent facts or numbers."
)

PROMPT = """Today's story clusters (most-covered first):
{stories}

Detected bursts:
{bursts}

Write the daily brief: a 2-sentence overview, then one bullet per story with its citation."""


def write_brief(
    stories: list[Story], bursts: list[dict], provider: LLMProvider | None = None
) -> dict:
    cfg = get_config()["brief"]
    provider = provider or get_provider()
    top = sorted(stories, key=lambda s: -len(s.article_ids))[: cfg["top_stories"]]
    stories_text = "\n".join(
        f"- {s.titles[0]} ({len(s.article_ids)} articles, {len(s.sources)} sources)" for s in top
    )
    bursts_text = (
        "\n".join(f"- {b['key']}: {b['today']} articles today" for b in bursts) or "(none)"
    )
    text = provider.complete(
        PROMPT.format(stories=stories_text, bursts=bursts_text),
        system=SYSTEM,
        max_tokens=cfg["max_tokens"],
    )
    return {
        "brief": text,
        "provider": provider.name,
        "stories_used": [s.story_id for s in top],
        "bursts": bursts,
    }
