"""Questions the app asks the database about movements: the yard's history."""
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Movement, VehicleContainer
from app.yard_day import YARD_TZ, day_start

CHECK_IN = "check_in"
MOVE = "move"
CHECK_OUT = "check_out"


def create_movement(
    session: Session,
    *,
    vehicle_container_id: int,
    kind: str,
    moved_by: int,
    from_slot_id: int | None = None,
    to_slot_id: int | None = None,
    appointment_id: int | None = None,
    reason: str | None = None,
) -> Movement:
    """Record one thing that happened to a vehicle/container. The caller commits."""
    movement = Movement(
        vehicle_container_id=vehicle_container_id,
        kind=kind,
        moved_by=moved_by,
        from_slot_id=from_slot_id,
        to_slot_id=to_slot_id,
        appointment_id=appointment_id,
        reason=reason,
    )
    session.add(movement)
    session.flush()
    return movement


def list_movements(
    session: Session,
    *,
    vehicle_container_id: int | None = None,
    from_day: date | None = None,
    to_day: date | None = None,
    haulier_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Movement]:
    """Return movements newest first, narrowed by the filters given.

    Days are the yard's days (Lagos). A deleted vehicle/container's history stays.
    """
    stmt = select(Movement)
    if vehicle_container_id is not None:
        stmt = stmt.where(Movement.vehicle_container_id == vehicle_container_id)
    if from_day is not None:
        stmt = stmt.where(Movement.moved_at >= day_start(from_day))
    if to_day is not None:
        stmt = stmt.where(Movement.moved_at < day_start(to_day + timedelta(days=1)))
    if haulier_id is not None:
        stmt = stmt.join(
            VehicleContainer, VehicleContainer.id == Movement.vehicle_container_id
        ).where(VehicleContainer.haulier_id == haulier_id)
    stmt = stmt.order_by(Movement.moved_at.desc(), Movement.id.desc()).limit(limit).offset(offset)
    return list(session.execute(stmt).scalars().all())


def count_movements_per_day(
    session: Session, *, from_day: date, to_day: date
) -> list[tuple[date, str, int]]:
    """Return (day, kind, count) for each yard day and kind that has movements, oldest first."""
    day = func.date(func.timezone(YARD_TZ.key, Movement.moved_at)).label("day")
    stmt = (
        select(day, Movement.kind, func.count().label("movements"))
        .where(
            Movement.moved_at >= day_start(from_day),
            Movement.moved_at < day_start(to_day + timedelta(days=1)),
        )
        .group_by(day, Movement.kind)
        .order_by(day, Movement.kind)
    )
    return [tuple(row) for row in session.execute(stmt).all()]


def list_last_movement_per_container(session: Session, *, until: datetime) -> list[Movement]:
    """Return each vehicle/container's latest movement before `until`, by vehicle/container id."""
    ranked = (
        select(
            Movement.id,
            func.row_number()
            .over(
                partition_by=Movement.vehicle_container_id,
                order_by=(Movement.moved_at.desc(), Movement.id.desc()),
            )
            .label("place"),
        )
        .where(Movement.moved_at < until)
        .subquery()
    )
    stmt = (
        select(Movement)
        .join(ranked, ranked.c.id == Movement.id)
        .where(ranked.c.place == 1)
        .order_by(Movement.vehicle_container_id)
    )
    return list(session.execute(stmt).scalars().all())