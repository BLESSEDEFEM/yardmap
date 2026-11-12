"""Questions the app and the report worker ask about report jobs."""
import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models import ReportJob

QUEUED = "queued"
RUNNING = "running"
DONE = "done"
FAILED = "failed"


def create_report_job(
    session: Session,
    *,
    requested_by: int,
    from_date: date,
    to_date: date,
    vehicle_container_id: int | None = None,
) -> ReportJob:
    """Add a queued report job and return it with its id and public_id. The caller commits."""
    job = ReportJob(
        requested_by=requested_by,
        from_date=from_date,
        to_date=to_date,
        vehicle_container_id=vehicle_container_id,
    )
    session.add(job)
    session.flush()
    return job


def get_report_job(session: Session, public_id: uuid.UUID) -> ReportJob | None:
    """Return the report job with this public id, or None. Safe: public_id is unique."""
    stmt = select(ReportJob).where(ReportJob.public_id == public_id)
    return session.execute(stmt).scalar_one_or_none()


def claim_report_job(session: Session, job_id: int) -> bool:
    """Mark a queued job as running, in one statement. True if this caller got it."""
    stmt = (
        update(ReportJob)
        .where(ReportJob.id == job_id, ReportJob.state == QUEUED)
        .values(state=RUNNING, started_at=func.now(), attempts=ReportJob.attempts + 1)
    )
    return session.execute(stmt).rowcount == 1


def finish_report_job(session: Session, job_id: int, *, file_location: str) -> bool:
    """Mark a running job as done, with where its file is. True if it was running."""
    stmt = (
        update(ReportJob)
        .where(ReportJob.id == job_id, ReportJob.state == RUNNING)
        .values(state=DONE, finished_at=func.now(), file_location=file_location)
    )
    return session.execute(stmt).rowcount == 1


def fail_report_job(session: Session, job_id: int, *, reason: str) -> bool:
    """Mark a running job as failed, with the reason in plain words. True if it was running."""
    stmt = (
        update(ReportJob)
        .where(ReportJob.id == job_id, ReportJob.state == RUNNING)
        .values(state=FAILED, finished_at=func.now(), failure_reason=reason)
    )
    return session.execute(stmt).rowcount == 1


def fail_abandoned_report_jobs(session: Session, *, now: datetime, running_for: timedelta) -> int:
    """Mark as failed every job running longer than `running_for` before `now`. Returns how many."""
    stmt = (
        update(ReportJob)
        .where(ReportJob.state == RUNNING, ReportJob.started_at < now - running_for)
        .values(state=FAILED, finished_at=now, failure_reason="abandoned: no worker finished it")
    )
    return session.execute(stmt).rowcount