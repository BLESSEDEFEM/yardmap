from fastapi import FastAPI
from app.config import settings

app = FastAPI()

vehicles_containers = [
    {"id": 1, "type": "container", "identifier": "MSKU4729301",
     "size": "standard", "haulier_id": 3, "status": "in_yard", "description": "40ft reefer", "current_slot_id": 12},
    {"id": 2, "type": "vehicle", "identifier": "LAG-442-KJA",
     "size": "large", "haulier_id": 3, "status": "registered", "description": None, "current_slot_id": None},
    {"id": 9, "type": "vehicle", "identifier": "KTP-442-KJA",
     "size": "small", "haulier_id": 5, "status": "registered", "description": None, "current_slot_id": None},
]

@app.get("/vehicles-containers")
def list_vehicles_containers():
    print(">>> list_vehicles_containers was called")
    return vehicles_containers


@app.get("/vehicles-containers/{vehicles_containers_id}")
def read_vehicle_container(vehicles_containers_id: int):
    for vehicle_container in vehicles_containers:
        if vehicle_container["id"] == vehicles_containers_id:
            return vehicle_container
    return {"detail": "not found"}


@app.get("/whoami")
def whoami():
    return {"app_name": settings.app_name}