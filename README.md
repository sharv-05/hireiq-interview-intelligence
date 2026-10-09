# HireIQ — Multimodal AI Interview Intelligence Platform

HireIQ is a production-shaped AI interview workspace for configuring structured interview rubrics, capturing candidate audio in the browser, transcribing and enriching answers, scoring responses, and reviewing hiring recommendations.

## What is included

- React 18 + TypeScript + Vite dashboard and candidate interview flow
- FastAPI + SQLAlchemy API with SQLite development database and PostgreSQL-ready configuration
- Server-side AI provider boundary (`mock` by default; OpenAI-compatible adapter available)
- Whisper-compatible transcription boundary with deterministic demo fallback
- PyDub normalization/chunking helper and Celery/Redis task entry points
- spaCy/VADER-compatible NLP enrichment with a dependency-light fallback
- YAML-configurable rubrics, seeded question bank, per-answer scoring
- ReportLab PDF report generation with radar chart, transcript, sentiment, and recommendation
- Docker Compose for API, worker, frontend, PostgreSQL, and Redis
- Pytest API coverage and Playwright smoke-test scaffold
- AI bias review, threat model, architecture diagram, and setup instructions

## Quick start (no API keys required)

```bash
cp .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8000

# new terminal
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The default demo mode uses local deterministic transcription/evaluation so the full experience works without paid services. Set `AI_PROVIDER=openai` and `OPENAI_API_KEY` only when you want live model scoring; the key is read by the API and never shipped to the browser.

## Docker

```bash
docker compose up --build
```

Frontend: http://localhost:4173  |  API docs: http://localhost:8000/docs

## API highlights

- `GET /api/questions` and `POST /api/questions`
- `GET /api/rubrics` and `POST /api/rubrics`
- `POST /api/sessions`, `GET /api/sessions`, `GET /api/sessions/{id}`
- `POST /api/sessions/{id}/responses` (audio upload or demo transcript)
- `GET /api/sessions/{id}/report` (PDF)

## Deployment

The API container is ready for Render/Railway-style deployment. Configure `DATABASE_URL`, `REDIS_URL`, `AI_PROVIDER`, and a server-side model key in the hosting provider's secret manager. Never commit `.env` or audio files.

## Architecture

See [`docs/architecture.md`](docs/architecture.md), [`docs/ai-bias-review.md`](docs/ai-bias-review.md), and [`docs/demo-script.md`](docs/demo-script.md).
