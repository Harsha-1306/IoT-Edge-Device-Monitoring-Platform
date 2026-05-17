from sqlalchemy import (
    Column, Integer, BigInteger, String, Float, DateTime, Boolean, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from datetime import datetime, timezone
from config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    device_id = Column(String(64), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    location = Column(String(120))
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(BigInteger, primary_key=True)
    device_id = Column(String(64), nullable=False, index=True)
    temperature = Column(Float)
    load_pct = Column(Float)
    position_x = Column(Float)
    position_y = Column(Float)
    recorded_at = Column(DateTime(timezone=True), default=utcnow, index=True)


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(BigInteger, primary_key=True)
    device_id = Column(String(64), nullable=False)
    metric = Column(String(32), nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    severity = Column(String(16), default="warning")
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, index=True)


def init_db():
    Base.metadata.create_all(engine)
