"""
Database models for use with SQLAlchemy
"""
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


class Lift(Base):
    """
    A lift at a ski resort
    """

    __tablename__ = "lifts"
    id = Column(String, primary_key=True)
    resort_id = Column(ForeignKey("resorts.id"))
    name = Column(String)
    unique_name = Column(String)
    status = Column(String)
    is_open = Column(Boolean)
    last_closed_on = Column(Date)
    last_opened_on = Column(Date)
    updated_at = Column(DateTime)


class Trail(Base):
    """
    A trail at a ski resort
    """

    __tablename__ = "trails"
    id = Column(String, primary_key=True)
    resort_id = Column(ForeignKey("resorts.id"))
    name = Column(String)
    unique_name = Column(String)
    trail_type = Column(String)
    status = Column(String)
    is_open = Column(Boolean)
    last_closed_on = Column(Date)
    last_opened_on = Column(Date)
    groomed = Column(Boolean)
    night_skiing = Column(Boolean)
    updated_at = Column(DateTime)
    rating = Column(Integer)

    def __init__(self, *args, **kwargs):
        if kwargs.get("name") and kwargs.get("trail_type"):
            self.unique_name = f"{kwargs.get('name')}_{kwargs.get('trail_type')}"
        super().__init__(*args, **kwargs)


class Resort(Base):
    """
    A ski resort
    """

    __tablename__ = "resorts"
    id = Column(String, primary_key=True)
    name = Column(String)
    parser_name = Column(String)
    trail_report_url = Column(String)
    snow_report_url = Column(String)
    updated_at = Column(DateTime)
    additional_wait_seconds = Column(Integer)
    total_trails = Column(Integer)
    open_trails = Column(Integer)
    total_lifts = Column(Integer)
    open_lifts = Column(Integer)
    city = Column(String)
    state = Column(String)
    snow_report = Column(JSONB)


class User(Base):
    """
    A user of the web application
    """

    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String)
    email_verified = Column(Boolean)
    created_at = Column(DateTime)
    hashed_password = Column(String)


class UserResort(Base):
    """
    A resort that is currently pinned by a particular user
    """

    __tablename__ = "user_resorts"
    user_id = Column(ForeignKey("users.id"), primary_key=True)
    resort_id = Column(ForeignKey("resorts.id"), primary_key=True)
