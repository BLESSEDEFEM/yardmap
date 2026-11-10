"""The one rule that picks a slot for a vehicle/container (DECISIONS.md #7)."""
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.crud import yard_slots
from app.models import YardSlot

KEEP_FREE_FOR=timedelta(hours=2)
SIZE_ORDER = {"small": 1, "standard": 2, "large": 3}

@dataclass(frozen=True)
class NoSlot:
    """Why no slot was picked and how many free slots were looked at."""
    
    reason: str
    candidates_considered : int


def pick_slot(free_slots: list[YardSlot], size: str) -> YardSlot | NoSlot:
    """Return the first free slot that accepts this size, or why there is none."""
    for slot in free_slots:
        if slot.accepts_size >= size:
            return slot
    if not free_slots:
        return NoSlot(reason="no free slot", candidates_considered=0)
    return NoSlot(reason=f"no free slot accepts size {size}", candidates_considered=len(free_slots))


def suggest_slot(
   session: Session, *, size: str, now: datetime, zone_id: int | None = None 
) -> YardSlot | NoSlot:
    """Fetch the free slots for the next KEEP_FREE_FOR, then apply the rule."""
    free_slots = yard_slots.list_free_slots(
        session, start=now, end=now + KEEP_FREE_FOR, zone_id=zone_id
    )
    return pick_slot(free_slots, size)


def fits(slot_size: str, box_size: str) -> bool:
    """True when a slot of slot_size can take a box of box_size."""
    return SIZE_ORDER[slot_size] >= SIZE_ORDER[box_size]