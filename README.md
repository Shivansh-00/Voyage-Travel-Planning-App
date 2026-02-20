# VoyageAI – Autonomous Travel Intelligence Engine

Production-grade AI Travel Intelligence Platform with multi-agent orchestration, RAG, optimization, and premium UI.

## Architecture

```text
[Next.js 14 Frontend]
   |  server/client actions
   v
[FastAPI Gateway + Middleware]
   |-> [Rate Limiter + Logging + Error Handling]
   |-> [Redis Cache]
   v
[LangGraph Orchestrator]
   -> PlannerAgent
   -> FlightIntelligenceAgent (mock API)
   -> HotelIntelligenceAgent (mock API)
   -> ExperienceAgent
   -> BudgetOptimizerAgent (OR-Tools)
   -> RiskAnalyzerAgent (weather mock API)
   -> MemoryAgent (Embeddings + VectorStore)
               |-> FAISS local
               |-> Pinecone abstraction
   v
[Structured Itinerary JSON]

[PostgreSQL] available for persistence and analytics extensions.
```

## Repo Layout

- `voyageai/backend`: FastAPI, LangGraph agents, caching, optimization, tests, Docker.
- `voyageai/frontend`: Next.js 14 App Router, Tailwind, Framer Motion, Recharts, tests.
- `voyageai/infra`: Nginx reverse proxy and CI pipeline.

## Quick Start

### Backend

```bash
cd voyageai/backend
cp .env.example .env
docker compose up --build
```

API:
- Health: `GET /health`
- Plan: `POST /api/v1/plan`

### Frontend

```bash
cd voyageai/frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` to backend endpoint if needed.

## Environment Variables

Defined in `voyageai/backend/.env.example`:
- `DATABASE_URL`
- `REDIS_URL`
- `VECTOR_PROVIDER` (`faiss`/`pinecone`)
- `PINECONE_*`
- `RATE_LIMIT`

## Deployment

1. Build backend Docker image.
2. Build frontend Next.js artifact.
3. Deploy with reverse proxy from `infra/nginx.conf`.
4. Use GitHub Actions workflow (`infra/github-actions.yml`) for CI.

## Scalability Notes

- Stateless API supports horizontal autoscaling.
- Redis cache reduces repeated orchestration cost.
- Vector abstraction supports migration from local FAISS to managed Pinecone.
- Async FastAPI and isolated agent modules enable concurrent plan generation.
- LangGraph typed state allows deterministic state transitions for observability.

## Future Improvements

- Add real supplier connectors (Amadeus, Booking, OpenWeather).
- Persist user profiles and trip history in PostgreSQL models.
- Add async background workflows for price monitoring.
- Add OpenTelemetry tracing and centralized log sink.
- Multi-region deployment with edge-cached itinerary rendering.
