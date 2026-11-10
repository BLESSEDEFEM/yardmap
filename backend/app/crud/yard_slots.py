"""Questions the app asks the database about yard slots."""
from datetime import datetime

from sqlalchemy import and_, exists, select
from sqlalchemy.orm import Session
from app.models import Appointment, VehicleContainer, YardSlot, User


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
    
    
def list_slots_with_occupant(
    session: Session,
    zone_id: int | None = None
) -> list[tuple[YardSlot, int | None]]:
    """Return every slot still in use with the id of what is parked in it, or None.

    Not paged, for the same reason as list_slots.
    """
    stmt = (
        select(YardSlot, VehicleContainer.id)
        .outerjoin(
            VehicleContainer,
            and_(
                VehicleContainer.current_slot_id == YardSlot.id, VehicleContainer.deleted_at.is_(None),
            ),
        )
        .where(YardSlot.deleted_at.is_(None))
    )
    if zone_id is not None:
        stmt = stmt.where(YardSlot.zone_id == zone_id)
    stmt = stmt.order_by(YardSlot.zone_id, YardSlot.label)
    return [(slot, occupant_id) for slot, occupant_id in session.execute(stmt).all()]


def list_free_slots(
    session: Session, *, start: datetime, end: datetime, zone_id: int | None = None
) -> list[YardSlot]:
    """Return every live slot that holds nothing and is held by no open appointment over [start, end).

    "Holds nothing" counts deleted vehicles/containers too: the database refuses a
    second row in a slot, deleted or not. One question, so the whole answer comes
    from one moment. Not paged.
    """
    held = exists().where(
        Appointment.slot_id == YardSlot.id,
        Appointment.status == "open",
        Appointment.reserved_from < end,
        Appointment.reserved_until > start,
    )
    stmt = (
        select(YardSlot)
        .outerjoin(VehicleContainer, VehicleContainer.current_slot_id == YardSlot.id)
        .where(YardSlot.deleted_at.is_(None), VehicleContainer.id.is_(None), ~held)
    )
    if zone_id is not None:
        stmt = stmt.where(YardSlot.zone_id == zone_id)
    stmt = stmt.order_by(YardSlot.zone_id, YardSlot.label)
    return list(session.execute(stmt).scalars().all())
