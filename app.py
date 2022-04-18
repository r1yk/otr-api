from datetime import datetime, timedelta

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from api.endpoints import router
from lib.auth import OTRAuth, JWT
from lib.postgres import get_api_db
import lib.schemas as schemas

app = FastAPI()
app.include_router(router)


@app.get("/")
def home():
    return "Hello from Open Trail Report"


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


@app.post("/login", response_model=schemas.Token)
async def login(db: Session = Depends(get_api_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user_email = form_data.username
    password = form_data.password
    user = OTRAuth(db).authenticate_user(user_email, password)
    new_jwt = JWT()
    token = new_jwt.create_token({
        'sub': user.id,
        'exp': (datetime.utcnow() + timedelta(minutes=30)).timestamp()
    })
    return {'access_token': token, 'token_type': 'bearer'}
