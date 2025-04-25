# TASK.md – GrandGuruAI Backlog

> **Legend:** ☐ open ☑ done 🛠 in‑progress

---
## Sprint 0 — Environment & Scaffold  (2025-04-24 → 2025-04-30)

| Task | Owner | Status |
|------|-------|--------|
| [ ] Initialize new Git repo (`grandguru-ai`) and create GitHub remote | Teo | |
| [ ] Open the repo in Cursor | Teo | |
| [ ] Install Python 3.11 via pyenv | Teo | |
| [ ] Set up Poetry & `poetry init` | Teo | |
| [ ] Install local Postgres **or** get Neon dev-branch URL | Teo | |
| [ ] Add core deps (`scrapy`, `langchain`, `pydantic-ai`, etc.) via Poetry | Teo | |
| [ ] Create `.env.example` and document required secrets | Assistant | |
| [ ] Scaffold directory tree (`crawler/`, `processors/`, etc.) | Assistant | |
| [ ] Add `pytest` skeleton + coverage config (80 %) | Assistant | |
| [ ] Push first commit to GitHub; CI (GitHub Actions) passes | Teo | |

### Discovered During Work
_(add new findings here)_


### Acceptance
`pytest -q` returns 0 failures; `scrapy crawl seed -V` prints version; `pnpm dev` starts Next app.

---
## Sprint 1  (Base Crawler & Extractors)   *ETA 3 days*
- [ ] Implement `DataItem` model in `crawler/items.py`
- [ ] Implement `BaseExtractor` + `GrandstreamExtractor`
- [ ] Seed spider crawling depth 1, writes `out.json`
- [ ] ItemRouter pipeline routes items to JSON or S3
- [ ] Unit tests: grandstream extractor happy/edge/failure

### Acceptance
`out.json` has ≥ 10 product items from grandstream.com.

---
## Sprint 2  (Processing & Vectorization)   *ETA 4 days*
- [ ] Alembic migration → products, documents tables
- [ ] `processors/ingest_worker.py` splits & embeds
- [ ] Pinecone index `grandguru-dev` receives vectors
- [ ] Postgres rows created via SQLAlchemy models
- [ ] Coverage ≥ 80 % for ingest utils

---
## Sprint 3  (API & Dashboard)   *ETA 4 days*
- [ ] FastAPI app with `/products`, `/crawl`, `/qa` routes
- [ ] WebSocket `/logs` stream
- [ ] Next.js dashboard pages: Crawler list, Search, Planner
- [ ] React Query hooks for crawlers & products

---
## Backlog / Next Sprints
- [ ] Pydantic‑AI planning agent (`/plan`)
- [ ] Auth (Clerk or Auth.js)
- [ ] Multi‑brand extractor plug‑ins (Cisco, TP‑Link, Ubiquiti)
- [ ] Deployment Terraform scripts (AWS Fargate)

---
## Discovered During Work
*(Add new TODOs here as they surface)*

---
*Last updated 2025‑04‑24*

