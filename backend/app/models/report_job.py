import uuid
from datetime import date, datetime

from sqlalchemy import (BigInteger, Date, DateTime, ForeignKey, Index, Text,
                        Uuid, func, text)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ReportJob(Base):
    """A JOB RECORD. One row per yard activity report somebody asked for."""

    __tablename__ = "report_jobs"
    __table_args__ = (
        Index(
            "one_live_report_per_request",
            "requested_by",
            "from_date",
            "to_date",
            unique=True,
            postgresql_where=text("state IN ('queued', 'running')"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, unique=True, server_default=text("gen_random_uuid()")
    )

    requested_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )
    from_date: Mapped[date] = mapped_column(Date)
    to_date: Mapped[date] = mapped_column(Date)
    vehicle_container_id: Mapped[int | None] = mapped_column(
        ForeignKey("vehicles_containers.id", ondelete="RESTRICT")
    )

    state: Mapped[str] = mapped_column(Text, server_default="queued")
    attempts: Mapped[int] = mapped_column(server_default="0")

    queued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    failure_reason: Mapped[str | None] = mapped_column(Text)
    file_location: Mapped[str | None] = mapped_column(Text)