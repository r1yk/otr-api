"""
FastAPI root
"""
from datetime import datetime, timedelta, timezone
import hashlib

from dotenv import dotenv_values

from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from nanoid import generate as generate_id

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.endpoints import authorize_new_user, router
from lib.auth import OTRAuth, JWT, HASH_METHOD
from lib.models import User
from lib.postgres import get_api_db
import lib.schemas as schemas

config = dotenv_values()

app = FastAPI()
app.include_router(router)


@app.get("/")
def home():
    """
    Root
    """
    return "Hello from Open Trail Report"


origins = [
    "http://localhost:3000",
    "http://localhost:3080",
    "https://opentrailreport.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["GET", "POST", "DELETE"],
)


@app.post(
    "/users", dependencies=[Depends(authorize_new_user)], response_model=schemas.User
)
async def create_user(
    new_user: schemas.NewUserRequest, db_session: Session = Depends(get_api_db)
):
    """
    Handle requests for new user registration
    """
    hashed_password = hashlib.new(HASH_METHOD, new_user.password.encode()).hexdigest()
    try:
        db_session.add(
            User(
                id=generate_id(),
                created_at=datetime.utcnow(),
                email=new_user.email,
                email_verified=False,
                hashed_password=hashed_password,
            )
        )
        db_session.commit()

    except IntegrityError:
        OTRAuth.return_status(400, detail="Email address already registered")


@app.post("/login", response_model=schemas.Token)
async def login(
    response: Response,
    db_session: Session = Depends(get_api_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Handle requests to login. Issue a new JWT upon success.
    """
    user_email = form_data.username
    password = form_data.password
    user = OTRAuth(db_session).authenticate_user(user_email, password)
    new_jwt = JWT()
    expires_at = round(
        (
            datetime.now(tz=timezone.utc)
            + timedelta(seconds=int(config.get("TOKEN_EXP_SECONDS", 3600)))
        ).timestamp()
    )
    token = new_jwt.create_token({"sub": user.id, "exp": expires_at})
    response.headers["Set-Cookie"] = f"otr_auth={token}; HttpOnly; Max-Age=3600"
    return {"access_token": token, "token_type": "bearer", "expires_at": expires_at}
