"""Dedup, clustering, and burst detection against planted ground truth."""

from trendscout.settings import get_config
from trendscout.stories.cluster import process
from trendscout.trends.burst import detect_bursts


def test_near_duplicates_folded(articles):
    _, labeled = process(articles)
    planted = labeled[labeled["is_near_dup"] == 1]
    linked_ids = set(labeled.loc[labeled["duplicate_of"].notna(), "article_id"]) | set(
        labeled["duplicate_of"].dropna().astype(int)
    )
    caught = planted["article_id"].isin(linked_ids).mean()
    assert caught >= 0.8, f"only {caught:.0%} of planted near-dups linked"


def test_clustering_groups_same_story(articles):
    stories, labeled = process(articles)
    # For each true story, its (non-dup) articles should mostly share a cluster.
    purity = []
    for _, group in labeled[labeled["is_near_dup"] == 0].groupby("true_story"):
        top_cluster = group["story_id"].value_counts().iloc[0]
        purity.append(top_cluster / len(group))
    mean_purity = sum(purity) / len(purity)
    assert mean_purity >= 0.7, f"cluster purity {mean_purity:.2f} too low"
    assert len(stories) >= labeled["true_story"].nunique() * 0.5


def test_stories_report_velocity_and_sources(articles):
    stories, _ = process(articles)
    top = max(stories, key=lambda s: len(s.article_ids))
    d = top.as_dict()
    assert d["n_articles"] >= 3
    assert d["n_sources"] >= 2
    assert d["velocity_per_hour"] > 0


def test_burst_detected_on_planted_day(articles):
    bursts = detect_bursts(articles, by="topic")
    assert any(b["key"] == "security" for b in bursts), f"planted burst missed: {bursts}"


def test_burst_requires_minimum_volume(articles):
    cfg = get_config()["trends"]
    quiet = articles[articles["topic"] != "security"]
    bursts = detect_bursts(quiet, by="topic")
    for b in bursts:
        assert b["today"] >= cfg["burst_min_articles"]
