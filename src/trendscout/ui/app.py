"""Streamlit demo: story feed, burst radar, daily brief."""

from __future__ import annotations

import os

import httpx
import pandas as pd
import streamlit as st

API_URL = os.environ.get("TRENDSCOUT_API_URL", "http://localhost:8100")

st.set_page_config(page_title="trendscout", page_icon="📰", layout="wide")
st.title("📰 trendscout")
st.caption("Story clustering, near-duplicate collapse, burst detection, cited daily briefs")


def _ok() -> bool:
    try:
        return httpx.get(f"{API_URL}/health", timeout=3).status_code == 200
    except httpx.HTTPError:
        return False


if not _ok():
    st.error(f"API not reachable at {API_URL}. Start it with `make api`.")
    st.stop()

tab_stories, tab_trends, tab_brief = st.tabs(["Stories", "Burst radar", "Daily brief"])

with tab_stories:
    r = httpx.get(f"{API_URL}/stories", timeout=120)
    if r.status_code != 200:
        st.warning(r.json().get("detail", r.text))
    else:
        for s in r.json():
            with st.expander(
                f"{s['headline']}  —  {s['n_articles']} articles / {s['n_sources']} sources "
                f"({s['velocity_per_hour']}/hr)"
            ):
                for t in s["titles"]:
                    st.markdown(f"- {t}")

with tab_trends:
    r = httpx.get(f"{API_URL}/trends", timeout=120)
    if r.status_code != 200:
        st.warning(r.json().get("detail", r.text))
    else:
        body = r.json()
        c1, c2 = st.columns(2)
        c1.metric("Articles ingested", body["n_articles"])
        c2.metric("Near-duplicates collapsed", body["n_near_duplicates"])
        if body["bursts"]:
            st.subheader("🔥 Bursting topics")
            st.dataframe(pd.DataFrame(body["bursts"]), use_container_width=True, hide_index=True)
        else:
            st.info("No bursts detected today.")

with tab_brief:
    provider = st.radio("Provider", ["ollama", "claude", "fake"], horizontal=True)
    if st.button("Write today's brief", type="primary"):
        with st.spinner(f"Writing with {provider}…"):
            r = httpx.post(f"{API_URL}/brief", json={"provider": provider}, timeout=300)
        if r.status_code != 200:
            st.error(r.json().get("detail", r.text))
        else:
            body = r.json()
            st.markdown(body["brief"])
            st.caption(f"provider: {body['provider']} · stories used: {body['stories_used']}")
