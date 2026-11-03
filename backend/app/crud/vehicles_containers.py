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


def create_vehicle_container(
    session: Session,
    *,
    type: str,
    identifier: str,
    size: str,
    haulier_id: int,
    description: str | None = None,
) -> VehicleContainer:
    """Add a new vehicle/container and return it with its id. The caller commits."""
    vehicle_container = VehicleContainer(
        type=type,
        identifier=identifier,
        size=size,
        haulier_id=haulier_id, description=description,
    )
    session.add(vehicle_container)
    session.flush()
    return vehicle_container


def move_to_slot(
    session: Session, vehicle_container: VehicleContainer, slot_id: int | None
) -> VehicleContainer:
    """Put the vehicle/container in this slot, or in no slot when slot_id is None. The caller commits."""
    vehicle_container.current_slot_id = slot_id
    session.flush()
    return vehicle_container


def set_status(
    session: Session,
    vehicle_container: VehicleContainer,
    status: str,
) -> VehicleContainer:
    """Change the vehicle/container's status. The caller commits."""
    vehicle_container.status = status
    session.flush()
    return vehicle_container