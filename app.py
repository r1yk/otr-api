from typing import List, Optional, Union

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, nulls_last

from lib.postgres import get_session
from lib.models import Lift, Resort, Trail, UserResort
import lib.schemas as schemas
from webscraper import scrape_resort

app = FastAPI()


async def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


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
    allow_methods=["GET", "POST", "DELETE"]
)


@app.get("/resorts", response_model=Union[List[schemas.ResortWithUser], List[schemas.Resort]])
def get_resorts(user: Optional[str] = None, db: Session = Depends(get_db)):
    if user:
        query = db.query(Resort, UserResort.user_id).join(
            UserResort,
            and_(UserResort.resort_id == Resort.id, UserResort.user_id == user),
            isouter=True
        ).order_by(nulls_last(UserResort.user_id), Resort.name.asc()
                   ).all()
        return [schemas.ResortWithUser(**q[0].__dict__, user_id=q[1]) for q in query]

    return db.query(Resort).order_by(
        Resort.name.asc()
    ).all()


@app.post("/resorts/{resort_id}/pin")
def pin_resort_by_id(resort_id: str, user: str,  db: Session = Depends(get_db)):
    db.add(
        UserResort(user_id=user, resort_id=resort_id)
    )
    db.commit()
    return {}


@app.delete("/resorts/{delete_resort_id}/pin")
def delete_resort_pin_by_id(delete_resort_id: str, user: str,  db: Session = Depends(get_db)):
    user_resort = db.query(UserResort).filter_by(
        resort_id=delete_resort_id, user_id=user
    ).one()
    db.delete(user_resort)
    db.commit()
    return {}


@app.post("/resorts/{resort_id}/scrape", response_model=schemas.Resort, include_in_schema=False)
def update_resort_by_id(resort_id: str,  db: Session = Depends(get_db)):
    scrape_resort(resort_id)
    return db.query(Resort).filter_by(id=resort_id).one()


@app.get("/resorts/{resort_id}", response_model=schemas.Resort)
def get_resort_by_id(resort_id: str,  db: Session = Depends(get_db)):
    return db.query(Resort).filter_by(id=resort_id).one()


@app.get("/resorts/{resort_id}/lifts", response_model=List[schemas.Lift])
def get_lifts_by_resort(resort_id: str,  db: Session = Depends(get_db)):
    return db.query(Lift).filter_by(resort_id=resort_id).order_by(
        Lift.is_open.desc(), Lift.name.asc()
    ).all()


@app.get("/resorts/{resort_id}/trails", response_model=List[schemas.Trail])
def get_trails_by_resort(resort_id: str,  db: Session = Depends(get_db)):
    return db.query(Trail).filter_by(resort_id=resort_id).order_by(
        Trail.rating.asc(), Trail.is_open.desc(), Trail.name.asc()
    ).all()
