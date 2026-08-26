# TrendScout — News Intelligence (Event Sourcing Architecture) <div align="center"> [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MLflow](https://img.shields.io/badge/MLflow-Registry-0194E2.svg?logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-blue.svg?logo=pytest&logoColor=white)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) </div> > **Real-time news intelligence and trend discovery platform architected around Event Sourcing — recording all narrative developments in an append-only event store and hydrating rebuildable analytical projections for topic volume, burst leaderboards, and story cluster lifecycles.** --- ## 🏛️ Architecture Pattern: Event Sourcing Architecture In evolving media landscapes, mutable database records erase narrative history (e.g. how a story developed from initial wire report to global breaking news). Changing clustering hyperparameters or burst formulas requires replaying historical event timelines. `trendscout` treats state as a sequence of immutable domain events stored in an **Append-Only Event Store**: ```mermaid
> **Note:** This is a portfolio project demonstrating software engineering patterns and ML concepts. Not intended for production use without further hardening. sequenceDiagram autonumber participant Feeds as RSS / Media Ingest participant Log as EventStore (Append-Only Log) participant VolProj as TopicVolumeProjection participant BurstProj as BurstLeaderboardProjection participant Client as Analytics API / UI Feeds->>Log: append(ArticleIngestedEvent) Feeds->>Log: append(StoryClusterFormedEvent) Feeds->>Log: append(BurstDetectedEvent) note over Log: Events are immutable, ordered, and permanent Log->>VolProj: apply(ArticleIngestedEvent) Log->>BurstProj: apply(BurstDetectedEvent) Client->>VolProj: get_topic_count("ai_safety") VolProj-->>Client: Returns 42 articles Client->>BurstProj: get_recent_bursts(limit=5) BurstProj-->>Client: Returns top velocity burst stories note over VolProj,BurstProj: Projections can be wiped & fully rebuilt anytime via replay
``` ### Event Sourcing Features
- **Deterministic Replayability**: `projection.rebuild_from_store(store)` hydrates any read model from zero by replaying historical events.
- **Time-Travel Auditing**: Inspect the exact state of breaking news clusters at any point in the past.
- **Decoupled Read Projections**: Add new analytical views without modifying the ingestion pipeline or mutating existing schemas. ### Module Organization
- **`events/contracts.py`**: Immutable domain event dataclasses (`ArticleIngestedEvent`, `StoryClusterFormedEvent`, `BurstDetectedEvent`, `TrendBriefGeneratedEvent`).
- **`events/store.py`**: `EventStore` append-only log with sequential indexing and typed streaming.
- **`projections/projections.py`**: Rebuildable read models (`TopicVolumeProjection`, `BurstLeaderboardProjection`).
- **`stories/cluster.py`**: Incremental single-pass story clustering.
- **`trends/burst.py`**: Statistical burst velocity detection.
- **`brief/daily.py`**: AI daily briefing synthesizer with citations. --- ## 📰 Core Methodologies & Trend Detection ### 1. MinHash LSH Deduplication
- Collapses syndicated wire stories in $O(1)$ lookup time using MinHash locality-sensitive hashing. ### 2. Statistical Burst Velocity Detection
- Compares current publication rate $N_{\text{today}}$ against trailing baseline $\mu_{\text{trailing}}$: $$\text{Velocity Ratio} = \frac{N_{\text{today}}}{\max(\mu_{\text{trailing}}, 1.0)}$$
- Triggers `BurstDetectedEvent` when velocity ratio exceeds threshold $\theta$. --- ## 🚀 Quickstart & Setup Guide ```bash
git clone https://github.com/jackson-marcus/trendscout.git
cd trendscout $env:UV_CACHE_DIR = "D:\ml-projects\.uv-cache"
uv sync --group dev # Run unit tests and event sourcing verification
uv run pytest -q
uv run ruff check . # Launch FastAPI (port :8100) + Streamlit newsfeed (port :8601)
make api
make ui
``` --- ## 📂 Repository Layout ```
trendscout/
├── configs/ # Burst thresholds, clustering params, LLM prompts
├── data/ # Sample news articles and feed snapshots
├── src/trendscout/ # Core Python package
│ ├── events/ # Event Sourcing: domain events, event store log
│ ├── projections/ # Rebuildable read models: topic counts, bursts
│ ├── stories/ # Incremental semantic clustering
│ ├── trends/ # Burst velocity detection
│ ├── brief/ # Autonomous briefing synthesizer
│ ├── api/ # FastAPI REST endpoints
│ └── ui/ # Streamlit intelligence dashboard
├── tests/ # Comprehensive Pytest suite covering event sourcing & clustering
├── docker-compose.yml
└── pyproject.toml
``` --- ## 👤 Author & Contact **Jackson Marcus**
- **Email:** [jackson.marcus.work@gmail.com](mailto:jackson.marcus.work@gmail.com)
- **Upwork:** [Jackson Marcus on Upwork](https://www.upwork.com/freelancers/~012235717501ad9c7b)
- **GitHub:** [@jackson-marcus](https://github.com/jackson-marcus) --- ## 👨‍💻 Author & Maintainer <div align="center"> ### **Jackson Marcus**
**Senior AI & Machine Learning Engineer**
*Building ML Systems, Agentic Architectures & Scalable Data Pipelines* [![GitHub Profile](https://img.shields.io/badge/GitHub-jackson--marcus-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jackson-marcus)
[![Upwork Portfolio](https://img.shields.io/badge/Upwork-Top%20Rated%20Plus-14A800?style=for-the-badge&logo=upwork&logoColor=white)](https://www.upwork.com/freelancers/~012235717501ad9c7b)
[![Email Contact](https://img.shields.io/badge/Email-wajahatanees41%40gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:wajahatanees41@gmail.com) 📍 *Byron, GA, USA* </div>
