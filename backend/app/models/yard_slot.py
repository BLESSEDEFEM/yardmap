from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class YardSlot(Base):
    __tablename__ = "yard_slots"
    __table_args__ = (
        UniqueConstraint("zone_id", "label", name="yard_slots_zone_id_label_key"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("yard_zones.id", ondelete="RESTRICT")
    )
    label: Mapped[str] = mapped_column(Text)
    accepts_size: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )