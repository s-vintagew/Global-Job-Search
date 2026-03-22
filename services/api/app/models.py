from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), index=True, nullable=False)
    company = Column(String(300), index=True)
    city = Column(String(200))
    country = Column(String(100), index=True)
    lat = Column(Float)
    lng = Column(Float)
    type = Column(String(50), index=True)           # remote, onsite, hybrid
    experience_level = Column(String(50), index=True) # junior, mid, senior
    salary = Column(String(200))
    description = Column(Text)
    tags = Column(Text)                               # comma-separated skills
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100), index=True)           # remoteok, remotive, etc.
    posted_date = Column(String(30))
    scraped_at = Column(DateTime, server_default=func.now())
