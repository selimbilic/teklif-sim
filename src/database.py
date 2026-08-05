"""
Database Persistence & History Management Module for TEKLİF-Sim (v3.0.0).
Uses SQLAlchemy ORM supporting SQLite (default) and PostgreSQL.
"""

import os
import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from src.logger import logger

Base = declarative_base()

class ProposalRecord(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proposal_id = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    customer_name = Column(String(128), nullable=True, index=True)
    customer_class = Column(String(64), nullable=True)
    aircraft_type = Column(String(64), nullable=True, index=True)
    fleet_size = Column(Integer, nullable=True)
    modification_type = Column(String(64), nullable=True, index=True)
    pricing_strategy = Column(String(64), nullable=True)
    currency = Column(String(8), default="USD")
    total_manhours = Column(Float, nullable=False)
    labor_cost = Column(Float, nullable=False)
    contingency_cost = Column(Float, nullable=False)
    materials_cost = Column(Float, nullable=False)
    testing_cost = Column(Float, nullable=False)
    total_price_usd = Column(Float, nullable=False)
    total_price_converted = Column(Float, nullable=False)
    deterministic_hash = Column(String(64), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "customer_name": self.customer_name or "N/A",
            "customer_class": self.customer_class or "N/A",
            "aircraft_type": self.aircraft_type or "N/A",
            "fleet_size": self.fleet_size or 1,
            "modification_type": self.modification_type or "N/A",
            "pricing_strategy": self.pricing_strategy or "N/A",
            "currency": self.currency,
            "total_manhours": self.total_manhours,
            "total_price_usd": self.total_price_usd,
            "total_price_converted": self.total_price_converted,
            "deterministic_hash": self.deterministic_hash,
        }


# Initialize DB Engine
def get_db_path() -> str:
    db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "teklif_sim.db")

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{get_db_path()}")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


import uuid

def save_proposal(
    customer_name: Optional[str],
    customer_class: Optional[str],
    aircraft_type: Optional[str],
    fleet_size: Optional[int],
    modification_type: Optional[str],
    pricing_strategy: str,
    currency: str,
    total_manhours: float,
    labor_cost: float,
    contingency_cost: float,
    materials_cost: float,
    testing_cost: float,
    total_price_usd: float,
    total_price_converted: float,
    deterministic_hash: str
) -> ProposalRecord:
    """Saves a newly calculated proposal quote into the database."""
    session = SessionLocal()
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        proposal_id = f"PROP-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        record = ProposalRecord(
            proposal_id=proposal_id,
            created_at=now,
            customer_name=customer_name,
            customer_class=customer_class,
            aircraft_type=aircraft_type,
            fleet_size=fleet_size,
            modification_type=modification_type,
            pricing_strategy=pricing_strategy,
            currency=currency,
            total_manhours=total_manhours,
            labor_cost=labor_cost,
            contingency_cost=contingency_cost,
            materials_cost=materials_cost,
            testing_cost=testing_cost,
            total_price_usd=total_price_usd,
            total_price_converted=total_price_converted,
            deterministic_hash=deterministic_hash
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        logger.info(f"Saved proposal {record.proposal_id} to database.")
        return record
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save proposal to DB: {e}")
        raise
    finally:
        session.close()


def list_proposals(limit: int = 50, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves proposal history records from database."""
    session = SessionLocal()
    try:
        query = session.query(ProposalRecord).order_by(ProposalRecord.created_at.desc())
        if search_query:
            sq = f"%{search_query}%"
            query = query.filter(
                (ProposalRecord.customer_name.ilike(sq)) |
                (ProposalRecord.aircraft_type.ilike(sq)) |
                (ProposalRecord.proposal_id.ilike(sq)) |
                (ProposalRecord.modification_type.ilike(sq))
            )
        records = query.limit(limit).all()
        return [r.to_dict() for r in records]
    finally:
        session.close()
