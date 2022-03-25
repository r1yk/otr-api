from typing import List, Optional

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from lib.postgres import get_session
from lib.models import Lift, Resort, Trail
import lib.schemas as schemas
from webscraper import scrape_resort

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
)


@app.get("/resorts/", response_model=List[schemas.Resort])
def get_resorts(db: Session = Depends(get_session)):
    resorts = db.query(Resort).all()
    return resorts


@app.post("/resorts/{resort_id}/scrape", response_model=schemas.Resort, include_in_schema=False)
def update_resort_by_id(resort_id: str, db: Session = Depends(get_session)):
    scrape_resort(resort_id)
    return db.query(Resort).filter_by(id=resort_id).one()


@app.get("/resorts/{resort_id}", response_model=schemas.Resort)
def get_resort_by_id(resort_id: str, db: Session = Depends(get_session)):
    return db.query(Resort).filter_by(id=resort_id).one()


@app.get("/resorts/{resort_id}/lifts", response_model=List[schemas.Lift])
def get_lifts_by_resort(resort_id: str, db: Session = Depends(get_session)):
    return db.query(Lift).filter_by(resort_id=resort_id).all()


@app.get("/resorts/{resort_id}/trails", response_model=List[schemas.Trail])
def get_trails_by_resort(resort_id: str, db: Session = Depends(get_session)):
    return db.query(Trail).filter_by(resort_id=resort_id).all()
