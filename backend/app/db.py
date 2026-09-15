import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import create_engine, String, Text, DateTime, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from .config import settings

logger = logging.getLogger("lenny.db")

engine = create_engine(settings.database_url, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


class Message(Base):
    """A single turn (user or assistant) inside a chat session."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(128), index=True)
    role: Mapped[str] = mapped_column(String(32))  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    provider: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    skill: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


def init_db() -> bool:
    """Create tables if needed. Never raises — the app must still start (in a
    degraded, DB-less mode) if Postgres isn't reachable yet."""
    try:
        Base.metadata.create_all(engine)
        return True
    except Exception:
        logger.exception("Database initialization failed; continuing without persistence")
        return False


def db_healthy() -> bool:
    try:
        with Session(engine) as session:
            session.execute(select(1))
        return True
    except Exception:
        logger.exception("Database health check failed")
        return False


def save_message(session_id: str, role: str, content: str,
                  provider: Optional[str] = None, skill: Optional[str] = None) -> None:
    """Best-effort persistence. A DB outage should degrade the app, not break chat."""
    try:
        with Session(engine) as session:
            session.add(Message(
                session_id=session_id, role=role, content=content,
                provider=provider, skill=skill,
            ))
            session.commit()
    except Exception:
        logger.exception("Failed to persist message for session %s", session_id)


def get_history(session_id: str, limit_turns: int) -> List[Message]:
    """Most recent `limit_turns` user+assistant messages, oldest first."""
    try:
        with Session(engine) as session:
            rows = session.execute(
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(Message.created_at.desc())
                .limit(limit_turns * 2)
            ).scalars().all()
            return list(reversed(rows))
    except Exception:
        logger.exception("Failed to load history for session %s", session_id)
        return []


def list_sessions() -> List[str]:
    try:
        with Session(engine) as session:
            rows = session.execute(
                select(Message.session_id).distinct()
            ).scalars().all()
            return list(rows)
    except Exception:
        logger.exception("Failed to list sessions")
        return []
