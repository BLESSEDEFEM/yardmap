"""Fill the database with starting rows."""
import sys

from sqlalchemy import select, text

from app.db import SessionLocal, engine
from app.models import YardSlot, YardZone

YARD_ZONES = [
    {"name": "Zone A"},
    {"name": "Zone B"},
]

YARD_SLOTS = [
    {"label": "A1", "accepts_size": "standard", "zone_name": "Zone A"},
    {"label": "A2", "accepts_size": "large", "zone_name": "Zone A"},
    {"label": "B1", "accepts_size": "small", "zone_name": "Zone B"},
]

def main() -> None:
    with SessionLocal() as session:
        zones_by_name = {}
        for row in YARD_ZONES:
            zone = session.execute(
                select(YardZone).where(YardZone.name == row["name"])
            ).scalar_one_or_none()
            if zone is None:
                zone = YardZone(**row)
                session.add(zone)
            zones_by_name[row["name"]] = zone
        session.flush()
        for row in YARD_SLOTS:
            zone = zones_by_name[row["zone_name"]]
            slot = session.execute(
                select(YardSlot).where(
                    YardSlot.zone_id == zone.id, YardSlot.label == row["label"]
                )
            ).scalar_one_or_none()
            if slot is None:
                session.add(YardSlot(zone_id=zone.id, label=row["label"], accepts_size=row["accepts_size"]))
        session.commit()
        
def wipe() -> None:
    with engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE report_jobs, movements, appointments, "
            "vehicles_containers, yard_slots, yard_zones RESTART IDENTITY"
        ))


if __name__ == "__main__":
    if "--wipe" in sys.argv:
        wipe()
    main()