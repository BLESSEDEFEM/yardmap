"""Questions the app asks the database about users."""
from sqlalchemy.orm import Session

from app.models import User


def get_user(session: Session, user_id: int) -> User | None:
    """Return the user with this id, or None if there is none."""
    return session.get(User, user_id)


def update_user(
    session: Session, user: User, *, role: str | None = None, status: str | None = None
) -> User:
    """Change only the fields given; leave the others as they are. The caller commits."""
    if role is not None:
        user.role = role
    if status is not None:
        user.status = status
    session.flush()
    return user