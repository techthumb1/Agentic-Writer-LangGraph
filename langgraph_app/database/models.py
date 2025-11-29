# File: langgraph_app/database/models.py
# Database models for analytics tracking
# RELEVANT FILES: analytics_endpoints.py, integrated_server.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class GenerationLog(Base):
    __tablename__ = 'generation_logs'
    
    id = Column(Integer, primary_key=True)
    template_id = Column(String(255), nullable=False, index=True)
    style_profile_id = Column(String(255), nullable=False, index=True)
    word_count = Column(Integer, nullable=False)
    generation_time_seconds = Column(Float, nullable=False)
    success = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/writerzroom")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create tables - call on startup"""
    Base.metadata.create_all(bind=engine)