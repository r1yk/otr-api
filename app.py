from typing import List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from lib.postgres import get_session
from lib.models import Lift, Resort, Trail
import lib.schemas as schemas
from webscraper import scrape_resort

app = FastAPI()


db = get_session()


@app.get("/")
def home():
    return {}


origins = [
    "http://localhost:3000",
    "http://localhost:3080",
    "https://opentrailreport.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
)


@app.get("/resorts", response_model=List[schemas.Resort])
def get_resorts():
    return db.query(Resort).order_by(
        Resort.name.asc()
    ).all()


@app.post("/resorts/{resort_id}/scrape", response_model=schemas.Resort, include_in_schema=False)
def update_resort_by_id(resort_id: str):
    scrape_resort(resort_id)
    return db.query(Resort).filter_by(id=resort_id).one()


@app.get("/resorts/{resort_id}", response_model=schemas.Resort)
def get_resort_by_id(resort_id: str):
    return db.query(Resort).filter_by(id=resort_id).one()


@app.get("/resorts/{resort_id}/lifts", response_model=List[schemas.Lift])
def get_lifts_by_resort(resort_id: str):
    return db.query(Lift).filter_by(resort_id=resort_id).order_by(
        Lift.is_open.desc(), Lift.name.asc()
    ).all()


@app.get("/resorts/{resort_id}/trails", response_model=List[schemas.Trail])
def get_trails_by_resort(resort_id: str):
    return db.query(Trail).filter_by(resort_id=resort_id).order_by(
        Trail.rating.asc(), Trail.is_open.desc(), Trail.name.asc()
    ).all()
