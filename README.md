# TrendScout — Real-Time News Intelligence & Trend Discovery Engine

<div align="center">

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MLflow](https://img.shields.io/badge/MLflow-Registry-0194E2.svg?logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-blue.svg?logo=pytest&logoColor=white)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

> **Real-time news intelligence pipeline: live RSS streaming, MinHash near-duplicate deduplication, single-pass incremental story clustering, Kleinberg-style burst detection, and AI daily briefings with inline citations.**

---

## 📖 Executive Summary & Value Proposition

**`trendscout`** is a production-grade, end-to-end machine learning system built with strict engineering discipline, reproducible pipelines, and enterprise MLOps best practices. It bridges the gap between theoretical statistical rigor and high-availability operational microservices.

## 📰 Core Methodologies & Real-Time NLP

### 1. MinHash LSH Near-Duplicate Deduplication
- Collapses syndicated wire stories and minor editorial rewrites in $O(1)$ lookup time using MinHash locality-sensitive hashing.

### 2. Single-Pass Online Incremental Story Clustering
- Groups incoming news items into evolving narrative clusters with dynamic cluster centroids and temporal decay.

### 3. Kleinberg Burst Detection
- Models publication velocity spikes to identify emerging market-moving stories before mainstream saturation.

### 4. Autonomous Daily Briefing Agent
- Generates structured executive summaries with inline markdown citations linking back to original news outlets.

## 📊 Architecture & Pipeline

```mermaid
flowchart LR
    RSS[Live RSS Media Streams] --> MinHash[MinHash LSH Deduplication]
    MinHash --> Cluster[Single-Pass Incremental Clustering]
    Cluster --> Burst[Kleinberg Burst Velocity Detector]
    Burst --> Agent[Autonomous Synthesis Briefing Agent]
    Agent --> API[FastAPI :8100] --> UI[Streamlit Newsfeed :8601]
```

## 🛠️ Tech Stack & Engineering Standards
- **NLP & Streaming:** Python 3.12, Feedparser, Sentence-Transformers, Claude / Ollama
- **Serving & UI:** FastAPI, Streamlit, MLflow
- **Testing:** Pytest verification of deduplication, clustering stability, and briefing synthesis


---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites & Environment Setup
Using **[uv](https://docs.astral.sh/uv/)** for lightning-fast, reproducible dependency resolution:

```bash
# Clone the repository
git clone https://github.com/jackson-marcus/trendscout.git
cd trendscout

# Install dependencies and pre-commit hooks
uv sync --group dev
```

### 2. Run Test Suite & Code Quality Checks
```bash
# Run unit & integration tests with coverage
uv run pytest --cov

# Run ruff linter and formatting checks
uv run ruff check .
uv run ruff format --check .
```

### 3. Launch Services Locally
```bash
# Start FastAPI REST API (listening on port :8100)
make api
# Or: uv run uvicorn trendscout.api.main:app --reload --port 8100

# Start interactive Streamlit dashboard (listening on port :8601)
make ui

# Launch local MLflow Experiment Tracking UI (listening on port :5010)
make mlflow
```

### 4. Run with Docker Compose
```bash
# Spin up the complete microservice stack
docker compose up --build
```

---

## 📂 Repository Layout

```
trendscout/
├── .github/workflows/ci.yml       # GitHub Actions CI pipeline (lint, test, build)
├── configs/                      # Configuration files and hyperparameters
├── data/                         # Data directory (raw, interim, processed)
├── scripts/                      # Data generators and operational scripts
├── src/trendscout/               # Core Python package
│   ├── api/                      # FastAPI routes, schemas, and endpoints
│   ├── models/                   # Statistical models, ML algorithms, and estimators
│   ├── ui/                       # Streamlit interactive application
│   └── settings.py               # Centralized configuration & environment loader
├── tests/                        # Comprehensive Pytest suite
├── docker-compose.yml            # Multi-service container orchestration
├── Dockerfile                    # Container definition for API service
├── Makefile                      # Standardized project tasks
└── pyproject.toml                # Pinned dependencies and tool configs
```

---

## 👤 Author & Contact

**Jackson Marcus**
- **Email:** [jackson.marcus.work@gmail.com](mailto:jackson.marcus.work@gmail.com)
- **Upwork:** [Jackson Marcus on Upwork](https://www.upwork.com/freelancers/~012235717501ad9c7b)
- **GitHub:** [@jackson-marcus](https://github.com/jackson-marcus)

*Available for machine learning engineering, MLOps, data science, and AI system architecture consulting and contract engagements.*

