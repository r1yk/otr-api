from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Lift(Base):
    __tablename__ = 'lifts'
    id = Column(String, primary_key=True)
    resort_id = Column(ForeignKey('resorts.id'))
    name = Column(String)
    unique_name = Column(String)
    status = Column(String)
    is_open = Column(Boolean)
    updated_at = Column(DateTime)


class Trail(Base):
    __tablename__ = 'trails'
    id = Column(String, primary_key=True)
    resort_id = Column(ForeignKey('resorts.id'))
    name = Column(String)
    unique_name = Column(String)
    trail_type = Column(String)
    status = Column(String)
    is_open = Column(Boolean)
    groomed = Column(Boolean)
    night_skiing = Column(Boolean)
    updated_at = Column(DateTime)
    icon = Column(String)

    def __init__(self, *args, **kwargs):
        if kwargs.get('name') and kwargs.get('trail_type'):
            self.unique_name = f"{kwargs.get('name')}_{kwargs.get('trail_type')}"
        super().__init__(*args, **kwargs)


class Resort(Base):
    __tablename__ = 'resorts'
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
