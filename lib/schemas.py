from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBase


class BaseModel(PydanticBase):
    class Config:
        orm_mode = True


class Resort(BaseModel):
    id: str
    city: str
    name: str
    open_lifts: int
    open_trails: int
    state: str
    total_lifts: int
    total_trails: int
    trail_report_url: str
    updated_at: datetime


class Lift(BaseModel):
    id: str
    name: str
    status: str
    updated_at: datetime


class Trail(BaseModel):
    id: str
    name: str
    icon: Optional[int]
    status: str
    is_open: bool
    night_skiing: bool
    groomed: Optional[bool]
    updated_at: datetime
