from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
    
    
class VehicleContainerCreate(BaseModel):
    type: Literal["vehicle", "container"]
    identifier: str = Field(min_length=1, max_length=50)
    size: Literal["small", "standard", "large"]
    haulier_id: int
    description: str | None = Field(default=None, max_length=500)
    
class VehicleContainerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    identifier: str
    size: str
    haulier_id: int
    description: str | None
    status: str
    
class VehicleContainerListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    identifier: str
    size: str
    haulier_id: int
    current_slot_id: int | None
    status: str