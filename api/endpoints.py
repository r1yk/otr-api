"""API endpoints"""
from typing import List, Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from lib.models import Lift, Resort, Trail
from lib.postgres import get_api_db
import lib.schemas as schemas


router = APIRouter()


@router.get(
    "/resorts", response_model=Union[List[schemas.ResortWithUser], List[schemas.Resort]]
)
def get_resorts(db_session: Session = Depends(get_api_db)):
    """Return all resorts"""
    return db_session.query(Resort).order_by(Resort.name.asc()).all()


@router.get("/resorts/{resort_id}", response_model=schemas.Resort)
def get_resort_by_id(resort_id: str, db_session: Session = Depends(get_api_db)):
    """Return a single resort"""
    return db_session.query(Resort).filter_by(id=resort_id).one()


@router.get("/resorts/{resort_id}/lifts", response_model=List[schemas.Lift])
def get_lifts_by_resort(resort_id: str, db_session: Session = Depends(get_api_db)):
    """Return all lifts for a given resort"""
    return (
        db_session.query(Lift)
        .filter_by(resort_id=resort_id)
        .order_by(Lift.is_open.desc(), Lift.name.asc())
        .all()
    )


@router.get("/resorts/{resort_id}/trails", response_model=List[schemas.Trail])
def get_trails_by_resort(resort_id: str, db_session: Session = Depends(get_api_db)):
    """Return all trails for a given resort"""
    return (
        db_session.query(Trail)
        .filter_by(resort_id=resort_id)
        .order_by(Trail.rating.asc(), Trail.is_open.desc(), Trail.name.asc())
        .all()
    )
