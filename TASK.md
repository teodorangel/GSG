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
## Sprint 1  (Base Crawler & Extractors)   *ETA 3 days*
- [x] [S1-01] DataItem model (items.py)   <!-- commit <SHA> -->
- [x] [S1-02] BaseExtractor interface
- [x] [S1-03] GrandstreamExtractor MVP
- [x] [S1-04] SeedSpider depth=1
- [x] [S1-05] Unit tests for extractor & data item
- [x] [S1-06] Enhanced GrandstreamExtractor to support multi-level extraction (categories, subcategories, series, articles, manuals) (2025-05-03)

### Acceptance
`out.json` has ≥ 10 product items from grandstream.com.

---
## Sprint 2  (Processing & Vectorization)   *ETA 4 days*
- [✓] Alembic migration → products, documents tables
- [x] `processors/ingest_worker.py` splits & embeds
- [✈] Pinecone index `grandguru-dev` receives vectors
- [✈] Postgres rows created via SQLAlchemy models
- [ ] Coverage ≥ 80  % for ingest utils

---
## Sprint 3  (API & Dashboard)   *ETA 4 days*
- [x] FastAPI app with `/products`, `/crawl`, `/qa` routes
- [x] WebSocket `/logs` stream
- [ ] Next.js dashboard pages: Crawler list, Search, Planner
- [ ] React Query hooks for crawlers & products

---
## Backlog / Next Sprints
- [ ] Pydantic‑AI planning agent (`/plan`)
- [ ] Auth (Clerk or Auth.js)
- [ ] Multi‑brand extractor plug‑ins (Cisco, TP‑Link, Ubiquiti)
- [ ] Deployment Terraform scripts (AWS Fargate)

## Sprint 4 – AI Agent & RAG Integration
- [ ] [S4-1] Pydantic-AI RetrievalQA Agent: implement `api/agent.py` with `@ai_function run_qa(query: str, product_id: Optional[int] = None) -> QAResponse` using LangChain's SQLDatabaseChain tool, Pinecone Retriever, and ReAct agent.
- [ ] [S4-1.1] Unit tests for `run_qa` in `tests/api/test_agent.py`, mocking SQL tool and Retriever, asserting the expected `QAResponse`.
- [ ] [S4-2] Planning Agent & `/plan` endpoint: extend API with project planning chain and endpoint.
  - [ ] [S4-2.1] Extend `api/models.py` with `PlanRequest` and `PlanResponse` schemas.
  - [ ] [S4-2.2] Create `api/routers/plan.py` with `create_plan` route using `run_plan`.
  - [ ] [S4-2.3] Add Pydantic-AI function `run_plan(product_ids: List[int], budget: float, site_size_sqft: int) -> PlanResponse` in `api/agent.py`.
  - [ ] [S4-2.4] Write unit tests in `tests/api/test_plan.py`, mocking database and Pinecone calls.

---
## Sprint 5 – Front-end Dashboard
- [ ] [S5-1] Scaffold Next.js 14 app with TypeScript, Tailwind CSS, and shadcn/ui
- [ ] [S5-1.1] Configure TanStack Query provider in `app/layout.tsx`
- [ ] [S5-1.2] Set up OpenAPI client using `openapi-typescript` or custom fetch hooks
- [ ] [S5-1.3] Create shared React Query hooks in `web/hooks/`:
  - `useProducts(skip, limit)` → GET `/products`
  - `useStartCrawl(params)` → POST `/crawl`
  - `useQA(query)` → POST `/qa`
  - `usePlan(payload)` → POST `/plan`
  - `useLogs(jobId)` → WebSocket subscription to `/logs/ws/{jobId}`

### Sprint 5.2 – Build Pages & Components
- [ ] [S5-2] `/products` page: data table with pagination and detail modal/page
- [ ] [S5-2.1] `/crawl` page: form for crawl parameters, start button, show job ID, live logs stream component
- [ ] [S5-2.2] `/qa` page: chat UI with input box, ask button, render answers and sources
- [ ] [S5-2.3] `/plan` page: multi-step wizard form (select products, budget, site size) and display plan results

## Discovered During Work
*(Add new TODOs here as they surface)*
- [ ] Update tests to use real Pinecone interaction instead of mocks
- [ ] Debug `test_tables_exist` failure in CI/local environment
- [ ] Investigate and fix JSON parsing error on line 107 of `out.jl` if it persists during real ingestion runs

---
*Last updated 2025‑05‑16*

