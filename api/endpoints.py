from typing import List, Union

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import and_, nulls_last
from sqlalchemy.orm import Session

from lib.auth import JWT, OTRAuth, WEB_APP_SECRET, SECRET_KEY
from lib.models import Lift, Resort, Trail, UserResort
from lib.postgres import get_api_db
import lib.schemas as schemas
from webscraper import scrape_resort


async def authorize_new_user(request: Request, authorization: str | None = Header(None)):
    """
    Handle requests to create new users. This can only be done by the web application.
    Make sure the `Authorization` header is present, and that the token was signed
    by the web application.
    """
    payload = await request.json()
    secret = f"otr-verify:{payload.get('email')}@{payload.get('password')}"
    return _authorize(request, authorization, secret, split_on='Bearer ')


def authorize(
        request: Request,
        authorization: str | None = Header(None),
        cookie: str | None = Header(None)):
    """Handle requests made on behalf of individual users."""
    token_header = cookie or authorization
    split_on = 'otr_auth=' if cookie else 'Bearer '
    return _authorize(request, token_header, secret=SECRET_KEY, split_on=split_on)


def _authorize(request: Request, bearer_token, secret: str = SECRET_KEY, split_on='otr_auth='):
    """
    Verify that a given bearer token is both unexpired and signed with a given secret. 
    """
    if not bearer_token:
        OTRAuth.return_status(401)

    components = bearer_token.split(split_on)
    if len(components) == 2:
        token = components[1]
        jwt = JWT(secret)
        message = jwt.decode_token(token)
        request.state.user_id = message['sub']
        return message

    OTRAuth.return_status(401)


def get_user_id(request: Request) -> str:
    return request.state.user_id


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(
    dependencies=[Depends(oauth2_scheme), Depends(authorize)]
)


@router.post("/logout")
async def logout(response: Response):
    response.headers['Set-Cookie'] = f'otr_auth=null; HttpOnly'
    return {'access_token': None, 'token_type': 'bearer'}


@router.get("/resorts", response_model=Union[List[schemas.ResortWithUser], List[schemas.Resort]])
def get_resorts(user_id: str = Depends(get_user_id), db: Session = Depends(get_api_db)):
    if user_id:
        # Join resorts with user_resorts when a user id is provided.
        query = db.query(Resort, UserResort.user_id).join(
            UserResort,
            and_(UserResort.resort_id == Resort.id,
                 UserResort.user_id == user_id),
            isouter=True
        ).order_by(
            nulls_last(UserResort.user_id), Resort.name.asc()
        ).all()
        return [
            schemas.ResortWithUser(
                **resort_with_user[0].__dict__,
                user_id=resort_with_user[1]
            )
            for resort_with_user in query
        ]

    # Return all resorts
    return db.query(Resort).order_by(
        Resort.name.asc()
    ).all()


@router.post("/resorts/{resort_id}/pin")
def pin_resort_by_id(
        resort_id: str,
        user_id: str = Depends(get_user_id),
        db: Session = Depends(get_api_db)):
    db.add(UserResort(user_id=user_id, resort_id=resort_id))
    db.commit()
    return {}


@router.delete("/resorts/{delete_resort_id}/pin")
def delete_resort_pin_by_id(
        delete_resort_id: str,
        user_id: str = Depends(get_user_id),
        db: Session = Depends(get_api_db)):
    user_resort = db.query(UserResort).filter_by(
        resort_id=delete_resort_id, user_id=user_id
    ).one()
    db.delete(user_resort)
    db.commit()
    return {}


@router.post("/resorts/{resort_id}/scrape", response_model=schemas.Resort, include_in_schema=False)
def update_resort_by_id(resort_id: str,  db: Session = Depends(get_api_db)):
    scrape_resort(resort_id)
    return db.query(Resort).filter_by(id=resort_id).one()


@router.get("/resorts/{resort_id}", response_model=schemas.Resort)
def get_resort_by_id(resort_id: str,  db: Session = Depends(get_api_db)):
    return db.query(Resort).filter_by(id=resort_id).one()


@router.get("/resorts/{resort_id}/lifts", response_model=List[schemas.Lift])
def get_lifts_by_resort(resort_id: str,  db: Session = Depends(get_api_db)):
    return db.query(Lift).filter_by(resort_id=resort_id).order_by(
        Lift.is_open.desc(), Lift.name.asc()
    ).all()


@router.get("/resorts/{resort_id}/trails", response_model=List[schemas.Trail])
def get_trails_by_resort(resort_id: str,  db: Session = Depends(get_api_db)):
    return db.query(Trail).filter_by(resort_id=resort_id).order_by(
        Trail.rating.asc(), Trail.is_open.desc(), Trail.name.asc()
    ).all()
