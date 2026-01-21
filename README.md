# Presentation Understanding Engine  
*Turn slide decks and PDFs into narrated, lesson‑style videos with summaries and optional quizzes.*

## Overview

Presentation Understanding Engine is a FastAPI + Next.js system that converts PPT/PPTX and PDF documents into narrated video lessons. It extracts slide/page content, produces summaries, generates narration using local TTS, and can optionally create quiz questions using a local or pluggable LLM.

### Key Capabilities

- Upload PPT/PPTX or PDF documents from a simple web UI.
- Parse slides/pages and extract structured content.
- Generate per‑slide/page summaries and narration scripts.
- Synthesize narration via local or pluggable TTS.
- Optionally generate quiz questions using a local LLM.
- Produce a stitched, narrated “video‑lesson” output.

## Features

- End‑to‑end pipeline: upload → parse → summarize → narrate → render.
- Local‑first AI integrations (LLM + TTS) with configurable providers.
- Real‑time job progress and result display in the UI.
- Clear separation of backend orchestration and frontend experience.

## Architecture

The system is split into a Next.js frontend and a FastAPI backend, with local storage for intermediate assets and outputs. A typical request flow is:

**Browser → Next.js → FastAPI → LLM/TTS + Storage → Frontend results**

High‑level components:

- **Frontend (Next.js):** Upload UI, progress tracking, results visualization.
- **Backend (FastAPI):** File ingestion, parsing, orchestration, pipeline execution.
- **LLM + TTS:** Pluggable local providers for summary, narration, and quizzes.
- **Storage:** Source files, intermediate assets, and final outputs.

## Project Structure

```text
.
├── backend/           # FastAPI application (API, services, LLM/TTS integration)
├── frontend/          # Next.js application (UI for upload and results)
├── data/              # Intermediate runtime data (local dev only)
├── docs/              # Architecture, configuration, and operational docs
├── samples/           # Example PPT/PPTX and PDF files
├── scripts/           # Helper scripts (dev, maintenance, profiling)
├── storage/           # Generated artifacts (local dev only; gitignored)
├── logs/              # Log output (local dev only; gitignored)
├── docker-compose.yml
├── LICENSE
└── README.md
```

## Getting Started

### Prerequisites

Backend:
- Python 3.11+
- pip / virtualenv

Frontend:
- Node.js 18+ (20+ recommended)
- npm / yarn / pnpm

Optional:
- Docker + Docker Compose (if running via containers)

### Installation

```bash
git clone <repo-url>
cd Presentation-Understanding-Engine
```

Backend setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements/requirements.txt
```

Frontend setup:

```bash
cd frontend
npm install
```

### Environment Configuration

Backend:

- Copy `backend/.env.example` to `backend/.env`
- Configure LLM/TTS provider settings, storage paths, limits, etc.

Frontend:

- Copy `frontend/.env.example` to `frontend/.env.local`
- Set the backend base URL and any client‑side config.

### Running Locally

Backend (from repo root):

```bash
uvicorn backend.app.main:app --reload
```

Frontend:

```bash
cd frontend
npm run dev
```

Open in browser:

- Frontend UI: http://localhost:3000  
- Backend API: http://localhost:8000  

## Usage

1. Start backend and frontend.
2. Open the web UI.
3. Upload a PPT/PPTX or PDF (see `samples/` for test files).
4. Configure options (summaries, narration, quizzes).
5. Run the pipeline.
6. View per‑slide/page results and download the narrated output.

Generated artifacts are stored in `storage/` for local development and are typically gitignored.

## Tech Stack

**Backend**
- FastAPI
- Python 3.11+
- Pydantic settings and structured config

**Frontend**
- Next.js
- React
- TypeScript (if enabled)

**AI**
- Local or pluggable LLM provider for summaries/quizzes
- Local or pluggable TTS provider for narration

## Testing & Quality

- Unit and integration tests target FastAPI endpoints and pipelines.
- Frontend testing focuses on critical flows (upload, progress, results).
- Linting/formatting (planned or recommended):
  - Python: Ruff + Black
  - Frontend: ESLint + Prettier

### CI (planned or recommended)

On each push/PR:
- Run backend tests
- Lint backend and frontend
- Check formatting

## Roadmap

- Async/background job queue for long‑running processing.
- Improved slide segmentation and content heuristics.
- Advanced quiz generation and answer validation.
- User accounts and persisted projects.
- Observability: logging, metrics, tracing.

## Contributing

- Open issues for bugs, feature requests, or questions.
- Submit PRs with clear descriptions and test coverage.
- Run linting/formatting and tests before opening a PR.

## License

MIT — see `LICENSE`.
