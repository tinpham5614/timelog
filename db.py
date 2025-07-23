# db.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()
engine = create_engine("sqlite:///timelog.db", echo=False)
SessionLocal = sessionmaker(bind=engine)


class TimeSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    project = Column(String, nullable=False)
    task = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.now(tz=timezone.utc))
    end_time = Column(DateTime, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)
