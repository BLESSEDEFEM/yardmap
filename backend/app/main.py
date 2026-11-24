from fastapi import Depends, FastAPI


from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import get_db
from app.routers import vehicles_containers as vc_router

app = FastAPI()
app.include_router(vc_router.router)


@app.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    one = db.execute(text("SELECT 1")).scalar()
    return {"database": "reachable", "answer": one}
