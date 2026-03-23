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

You can run the application either using Docker Compose (recommended) or locally.

### Using Docker Compose

```bash
# Clone & launch all services
docker compose up --build -d

# Wait ~30s for initial scrape, then open:
# http://localhost:3000
```

### Running Locally

**Prerequisites:**
- Python 3.12+
- PostgreSQL Server running

1. **Database Setup**
   Ensure PostgreSQL is running and a database named `global_jobs` is created based on your `.env` configuration.

2. **Run the API (Backend)**
   In a new terminal:
   ```bash
   cd services/api
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Run the FastAPI server
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

3. **Run the Scraper Worker (Backend)**
   In a new terminal window:
   ```bash
   cd services/scraper
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Set the PYTHONPATH to the current directory to recognize the app package
   PYTHONPATH=. python3 app/main.py
   ```

4. **Run the Frontend**
   In another terminal window:
   ```bash
   cd services/frontend/public
   
   # Start a simple HTTP server
   python3 -m http.server 3000
   ```
   Then open:
   `http://localhost:3000`

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
