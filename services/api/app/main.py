from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app import models, schemas
from app.database import SessionLocal, engine

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Global Jobs API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Health ──────────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# ─── Statistics ──────────────────────────────────────────────
@app.get("/api/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total_jobs = db.query(func.count(models.Job.id)).scalar() or 0
    total_countries = (
        db.query(func.count(func.distinct(models.Job.country)))
        .filter(models.Job.country.isnot(None), models.Job.country != "")
        .scalar()
        or 0
    )
    total_sources = (
        db.query(func.count(func.distinct(models.Job.source)))
        .filter(models.Job.source.isnot(None))
        .scalar()
        or 0
    )
    return schemas.StatsResponse(
        total_jobs=total_jobs,
        total_countries=total_countries,
        total_sources=total_sources,
    )


# ─── Countries ───────────────────────────────────────────────
@app.get("/api/countries", response_model=List[str])
def get_countries(db: Session = Depends(get_db)):
    results = (
        db.query(models.Job.country)
        .distinct()
        .filter(models.Job.country.isnot(None), models.Job.country != "")
        .order_by(models.Job.country)
        .all()
    )
    return [r[0] for r in results]


# ─── Jobs (filtered + paginated) ────────────────────────────
@app.get("/api/jobs", response_model=List[schemas.JobResponse])
def get_jobs(
    country: Optional[str] = None,
    type: Optional[str] = None,
    q: Optional[str] = None,
    days: Optional[int] = None,
    experience: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(200, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.Job)

    if country and country != "all":
        query = query.filter(models.Job.country == country)

    if type and type != "all":
        query = query.filter(models.Job.type == type)

    if q:
        search = f"%{q}%"
        query = query.filter(
            models.Job.title.ilike(search)
            | models.Job.company.ilike(search)
            | models.Job.tags.ilike(search)
        )

    if days:
        cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        query = query.filter(models.Job.posted_date >= cutoff)

    if experience and experience != "all":
        query = query.filter(models.Job.experience_level == experience)

    if source and source != "all":
        query = query.filter(models.Job.source == source)

    return query.order_by(models.Job.id.desc()).offset(offset).limit(limit).all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
