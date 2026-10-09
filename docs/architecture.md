# HireIQ architecture

```mermaid
flowchart LR
  Browser[React interview + hiring dashboard] --> API[FastAPI API]
  API --> DB[(PostgreSQL / SQLite)]
  API --> Queue[Celery + Redis]
  Queue --> Audio[PyDub normalization + Whisper adapter]
  Queue --> Eval[Rubric evaluator + LLM adapter]
  Eval --> NLP[spaCy / VADER enrichment]
  API --> PDF[ReportLab PDF report]
```

Audio is received as an upload, normalized and processed asynchronously in production. The demo path supplies a deterministic transcript when no audio/model provider is configured, making the complete UI testable without credentials. All model calls belong behind the API boundary.
