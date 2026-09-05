"""SQLite Database & Logging using SQLAlchemy"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./prime_records.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PrimeExecutionLog(Base):
    """
    Database model to record each prime execution.
    Stores:
    - timestamp: Execution UTC datetime
    - range_start & range_end: Range provided by the user
    - time_elapsed_ms: Execution duration in milliseconds
    - algorithm_chosen: Strategy used (e.g., Segmented Sieve, Classic Sieve)
    - primes_count: Total number of primes returned
    - request_type: Request mode ('range', 'check', 'nth')
    """
    __tablename__ = "prime_execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    range_start = Column(Integer, nullable=True)
    range_end = Column(Integer, nullable=True)
    time_elapsed_ms = Column(Float, nullable=False)
    algorithm_chosen = Column(String, nullable=False)
    primes_count = Column(Integer, default=0)
    request_type = Column(String, default="range")
    details = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)


def log_execution(
    algorithm_chosen: str,
    time_elapsed_ms: float,
    primes_count: int,
    range_start: Optional[int] = None,
    range_end: Optional[int] = None,
    request_type: str = "range",
    details: Optional[str] = None
) -> None:
    """Safely log execution record with guaranteed connection closing."""
    db = SessionLocal()
    try:
        entry = PrimeExecutionLog(
            timestamp=datetime.utcnow(),
            range_start=range_start,
            range_end=range_end,
            time_elapsed_ms=round(time_elapsed_ms, 3),
            algorithm_chosen=algorithm_chosen,
            primes_count=primes_count,
            request_type=request_type,
            details=details
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def get_recent_logs(limit: int = 20) -> List[PrimeExecutionLog]:
    """Retrieve recent executions."""
    db = SessionLocal()
    try:
        return db.query(PrimeExecutionLog).order_by(PrimeExecutionLog.id.desc()).limit(limit).all()
    finally:
        db.close()


