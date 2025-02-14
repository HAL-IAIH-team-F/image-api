from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from env import ENV
from util import fastapiutil

print("init")
# build
# uvicorn main:app

app = FastAPI()

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=ENV.cors_list.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# MongoDB Client
client = MongoClient(f"mongodb://{ENV.db_user}:{ENV.db_pass}@{ENV.db_host}:27017/")
db = client["image_database"]
collection = db["images"]
templates = Jinja2Templates(directory="templates")


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


fastapiutil.handler(app)
# noinspection PyUnresolvedReferences
import upload
# noinspection PyUnresolvedReferences
import prefernce
# noinspection PyUnresolvedReferences
import file
