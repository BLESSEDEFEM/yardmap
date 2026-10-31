"""Questions the app asks the database about yard slots."""
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from app.models import VehicleContainer, YardSlot


def get_slot(
    session: Session,
    slot_id: int,
) -> YardSlot | None:
    """Return the yard slot with this id, or None if there is none."""
    return session.get(YardSlot, slot_id)

def list_slots(
    session: Session,
    zone_id: int | None = None,
) -> list[YardSlot]:
    """Return every slot still in use, by zone then label.

    Not paged: a yard has a fixed number of slots and the map needs all of them.
    """
    stmt = select(YardSlot).where(YardSlot.deleted_at.is_(None))
    if zone_id is not None:
        stmt = select(YardSlot).where(YardSlot.zone_id == zone_id)
    stmt = stmt.order_by(YardSlot.zone_id, YardSlot.label)
    return list(session.execute(stmt).scalars().all())
    