"""
Schema objects to be used with FastAPI + Pydantic
"""
from datetime import datetime, date
from typing import Union, Optional
from pydantic import BaseModel as PydanticBase  # pylint: disable=no-name-in-module


class BaseModel(PydanticBase):
    """
    Base model inherited by all schema objects
    """

    class Config:
        """
        This wires up SQLAlchemy + FastAPI, such that functions serving API endpoints
        can just return the result of a SQLAlchemy query.
        """

        orm_mode = True


class NewUserRequest(BaseModel):
    """
    A JSON payload that represents a newly created user
    """

    email: str
    password: str


class User(BaseModel):
    """
    A user of the web application
    """

    id: str
    email: str
    email_verified: bool
    created_at: datetime


class Resort(BaseModel):
    """
    A ski resort
    """

    id: str
    city: str
    name: str
    open_lifts: int
    open_trails: int
    snow_report_url: Optional[str]
    state: str
    total_lifts: int
    total_trails: int
    trail_report_url: str
    updated_at: datetime
    snow_report: Union[dict, None]


class ResortWithUser(Resort):
    """
    A ski resort that also has a user_id?
    """

    user_id: Union[str, None]


class Lift(BaseModel):
    """
    A chairlift at a ski resort
    """

    id: str
    name: str
    status: str
    is_open: bool
    last_closed_on: Optional[date]
    last_opened_on: Optional[date]
    updated_at: datetime


class Trail(BaseModel):
    """
    A trail at a ski resort
    """

    id: str
    name: str
    rating: Optional[int]
    status: str
    is_open: bool
    last_closed_on: Optional[date]
    last_opened_on: Optional[date]
    night_skiing: bool
    groomed: Optional[bool]
    updated_at: datetime


class UserResorts(BaseModel):
    """
    A resort that is currently pinned by a particular user
    """

    id: str
    resort_id: str
    user_id: str
    created_at: datetime


class Token(BaseModel):
    """
    A JWT
    """

    access_token: str
    token_type: str
    expires_at: int
