"""Brief agent grounding + API contract."""

import pytest
from fastapi.testclient import TestClient

import trendscout.api.routes as routes
from trendscout.api.main import create_app
from trendscout.brief.write import write_brief
from trendscout.llm.base import FakeProvider
from trendscout.settings import get_config
from trendscout.stories.cluster import process
from trendscout.trends.burst import detect_bursts


def test_brief_grounded_in_stories(articles):
    stories, _ = process(articles)
    bursts = detect_bursts(articles)
    provider = FakeProvider(canned="Overview. - item [3 sources]")
    result = write_brief(stories, bursts, provider=provider)
    prompt = provider.calls[0]["prompt"]
    top = max(stories, key=lambda s: len(s.article_ids))
    assert top.titles[0] in prompt
    assert result["stories_used"]


@pytest.fixture()
def client(articles, tmp_path):
    cfg = get_config()
    original = cfg["data"]["articles_path"]
    path = tmp_path / "articles.parquet"
    articles.to_parquet(path, index=False)
    cfg["data"]["articles_path"] = str(path)
    routes.invalidate()
    yield TestClient(create_app())
    cfg["data"]["articles_path"] = original
    routes.invalidate()


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_stories_endpoint(client):
    body = client.get("/stories").json()
    assert body and body[0]["n_articles"] >= body[-1]["n_articles"]


def test_trends_endpoint(client):
    body = client.get("/trends").json()
    assert body["n_articles"] > 0
    assert body["n_near_duplicates"] > 0


def test_brief_endpoint_fake(client):
    r = client.post("/brief", json={"provider": "fake"})
    assert r.status_code == 200
    assert r.json()["provider"] == "fake"
