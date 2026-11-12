from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Movement(Base):
    __tablename__ = "movements"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('check_in', 'move', 'check_out')",
            name="movements_kind_check",
        ),
        Index(
            "movements_one_check_in_per_appointment",
            "appointment_id",
            unique=True,
            postgresql_where=text("kind = 'check_in'"),
        ),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    vehicle_container_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles_containers.id", ondelete="RESTRICT")
    )
    kind: Mapped[str] = mapped_column(Text)
    from_slot_id: Mapped[int | None] = mapped_column(
        ForeignKey("yard_slots.id", ondelete="RESTRICT")
    )
    to_slot_id: Mapped[int | None] = mapped_column(
        ForeignKey("yard_slots.id", ondelete="RESTRICT")
    )
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id", ondelete="RESTRICT")
    )
    reason: Mapped[str | None] = mapped_column(Text)
    
    moved_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )
    moved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
