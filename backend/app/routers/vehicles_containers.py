from fastapi import APIRouter, Depends, HTTPException
from typing import Literal

from sqlalchemy.orm import Session

from app.schemas.vehicles_containers import VehicleContainerCreate, VehicleContainerOut, VehicleContainerListItem
from app.crud import users, vehicles_containers


from app.db import get_db

router = APIRouter()

@router.post("/vehicles-containers", status_code=201, response_model=VehicleContainerOut)
def create_vehicle_container(body: VehicleContainerCreate, db: Session = Depends(get_db)):
    haulier = users.get_user(db, body.haulier_id)
    if haulier is None:
        raise HTTPException(status_code=404, detail="no user with that haulier_id")
    if haulier.role != "haulier":
        raise HTTPException(status_code=409, detail="that user is not a haulier")
    
    vehicle_container = vehicles_containers.create_vehicle_container(
        db,
        type=body.type,
        identifier=body.identifier,
        size=body.size,
        haulier_id=body.haulier_id,
        description=body.description,
    )
    
    db.commit()
    return vehicle_container


@router.get("/vehicles-containers", status_code=200, response_model=list[VehicleContainerListItem])
def list_vehicles_containers(db: Session = Depends(get_db), type: Literal["vehicle","container"] | None = None, status: Literal["registered","in_yard","departed"] | None = None, haulier_id: int | None = None):
    vehicle_container_list = vehicles_containers.list_vehicles_containers(db, type=type, status=status, haulier_id=haulier_id)
    return vehicle_container_list