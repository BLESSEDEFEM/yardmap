"""Questions the app asks the database about appointments."""
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Appointment, VehicleContainer
from app.yard_day import day_window


def list_overlapping_appointments(
   session: Session, slot_id: int, *, start: datetime, end: datetime
) -> list[Appointment]:
    """Return the open appointments in this slot whose window overlaps [start, end), earliest first."""
    stmt = (
        select(Appointment)
        .where(
            Appointment.slot_id == slot_id,
            Appointment.status == "open",
            Appointment.reserved_from < end,
            Appointment.reserved_until > start,
        )
        .order_by(Appointment.reserved_from, Appointment.id)
    )
    return list(session.execute(stmt).scalars().all())


def create_appointment(
    session: Session,
    *,
    vehicle_container_id: int,
    slot_id: int,
    reserved_from: datetime,
    reserved_until: datetime,
    created_by: int,
    notes: str | None = None,
) -> Appointment:
    """Add a new appointment and return it with its id. The caller commits."""
    appointment = Appointment(
        vehicle_container_id=vehicle_container_id,
        slot_id=slot_id,
        reserved_from=reserved_from,
        reserved_until=reserved_until,
        created_by=created_by,
        notes=notes,   
    )
    session.add(appointment)
    session.flush()
    return appointment


def get_open_appointment_for(
    session: Session, vehicle_container_id: int,
) -> Appointment | None:
    """Return this vehicle/container's open appointment, or None.

    At most one can exist: appointments_one_open_per_vehicle_container.
    """
    stmt = select(Appointment).where(
        Appointment.vehicle_container_id == vehicle_container_id,
        Appointment.status == "open",
    )
    return session.execute(stmt).scalar_one_or_none()


def get_appointment(session: Session, appointment_id: int) -> Appointment | None:
    """Return the appointment with this id, or None if there is none."""
    return session.get(Appointment, appointment_id)


def list_appointments(
    session: Session,
    *,
    status: str | None = None,
    day: date | None = None,
    haulier_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Appointment]:
    """Return appointments earliest first, narrowed by the filters given.

    A day is the yard's day (Lagos); an appointment is on a day when its window overlaps it.
    """
    stmt = select(Appointment)
    if status is not None:
        stmt = stmt.where(Appointment.status == status)
    if day is not None:
        start, end = day_window(day)
        stmt = stmt.where(Appointment.reserved_from < end, Appointment.reserved_until > start)
    if haulier_id is not None:
        stmt = stmt.join(
            VehicleContainer, VehicleContainer.id == Appointment.vehicle_container_id
        ).where(VehicleContainer.haulier_id == haulier_id)
    stmt = stmt.order_by(Appointment.reserved_from, Appointment.id).limit(limit).offset(offset)
    return list(session.execute(stmt).scalars().all())
