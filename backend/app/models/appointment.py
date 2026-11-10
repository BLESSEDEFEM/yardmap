from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Text, func, text
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        ExcludeConstraint(
            ("slot_id", "="),
            (func.tstzrange(text("reserved_from"), text("reserved_until")), "&&"),
            name="appointments_no_overlapping_open_window",
            using="gist",
            where=text("status = 'open'"),
        ),
        Index(
            "appointments_one_open_per_vehicle_container",
            "vehicle_container_id",
            unique=True,
            postgresql_where=text("status = 'open'"),
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_container_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles_containers.id", ondelete="RESTRICT")
    )
    slot_id: Mapped[int] = mapped_column(
        ForeignKey("yard_slots.id", ondelete="RESTRICT")
    )
    reserved_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    reserved_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, server_default="open")
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    