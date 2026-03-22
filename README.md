# 🌍 Global Job Search

Discover real-time job opportunities from around the world on an interactive 3D globe.

## Architecture

| Service | Tech | Port |
|---------|------|------|
| **Database** | PostgreSQL 16 | 5432 (internal) |
| **API** | FastAPI (Python 3.12) | 8000 |
| **Scraper** | Python 3.12 + APScheduler | — |
| **Frontend** | Globe.gl + Nginx | 3000 |

## Quick Start

```bash
# Clone & launch all services
docker compose up --build -d

# Wait ~30s for initial scrape, then open:
# http://localhost:3000
```

## Job Sources

- [RemoteOK](https://remoteok.com) — Remote jobs worldwide
- [Remotive](https://remotive.com) — Curated remote positions
- [Arbeitnow](https://arbeitnow.com) — European job listings
- [JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) — (Optional, needs `RAPIDAPI_KEY`)

## Environment Variables

Copy `.env` and customise:

| Variable | Default | Required |
|----------|---------|----------|
| `POSTGRES_USER` | `jobsearch` | ✅ |
| `POSTGRES_PASSWORD` | `jobsearch_pass` | ✅ |
| `POSTGRES_DB` | `global_jobs` | ✅ |
| `RAPIDAPI_KEY` | — | ❌ |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List jobs (filterable) |
| GET | `/api/countries` | Distinct countries |
| GET | `/api/stats` | Aggregate statistics |
| GET | `/api/health` | Liveness check |

### Filter Parameters (`/api/jobs`)

`country`, `type`, `q` (keyword), `days`, `experience`, `limit`, `offset`
