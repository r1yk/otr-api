"""
FastAPI root
"""
from dotenv import dotenv_values

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints import router


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
    allow_headers=["*"],
    allow_methods=["GET"],
)
