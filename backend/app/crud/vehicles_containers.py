"""Questions the app asks the database about vehicles and containers."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import VehicleContainer

def get_vehicle_container(session: Session, vehicle_container_id: int) -> VehicleContainer | None:
    """Return the vehicle/container with this id, or None if there is none."""
    return session.get(VehicleContainer, vehicle_container_id)

def list_vehicles_containers(
    session: Session,
    type: str | None = None,
    status: str | None = None,
    haulier_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[VehicleContainer]:
    """Return vehicles/containers in identifier order, narrowed by the filters given."""
    stmt = select(VehicleContainer).where(VehicleContainer.deleted_at.is_(None))
    if type is not None:
        stmt = stmt.where(VehicleContainer.type == type)
    if status is not None:
        stmt = stmt.where(VehicleContainer.status == status)
    if haulier_id is not None:
        stmt = stmt.where(VehicleContainer.haulier_id == haulier_id)
    stmt = stmt.order_by(VehicleContainer.identifier).limit(limit).offset(offset)
    return list(session.execute(stmt).scalars().all())


def count_vehicles_containers(session: Session) -> int:
    """Return how many vehicles/containers exist, leaving out deleted ones."""
    stmt = select(func.count()).select_from(VehicleContainer).where(
        VehicleContainer.deleted_at.is_(None)
    )
    return session.execute(stmt).scalar_one()