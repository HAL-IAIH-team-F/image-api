import io
import traceback
from typing import Union

from bson import Binary
from fastapi import FastAPI, HTTPException
from fastapi import File, UploadFile, Query
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient, errors
from starlette.middleware.cors import CORSMiddleware

import bodies
import reses
from data import JwtTokenData
from env import ENV
from tokens import *
from util import err

print("init")
# build
# uvicorn main:app

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ENV.cors_list.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# MongoDB Client
client = MongoClient(f"mongodb://{ENV.db_user}:{ENV.db_pass}@localhost:27017/")
db = client["image_database"]
collection = db["images"]
templates = Jinja2Templates(directory="templates")


@app.post("/upload/")
async def upload_image(
        file: UploadFile = File(...),
        token: JwtTokenData | None = Depends(get_token)
) -> reses.TokenRes:
    if token.token_type != "Upload":
        raise err.ErrorIds.INVALID_TOKEN.to_exception(f"invalid token type: {token.token_type}")
    file_content = await file.read()
    dt_now = datetime.now()

    image_data = {
        "uuid": token.uuid.__str__(),
        "original_filename": file.filename,
        "file_data": Binary(file_content),
        "upload_date": dt_now,
        "state": "Temp"
    }
    try:
        collection.insert_one(image_data)
    except errors.PyMongoError as e:
        traceback.print_exc()
        raise err.ErrorIds.PY_MONGO_ERROR.to_exception(e.__str__())

    return reses.TokenRes.create(token.uuid)


@app.put("/preference/{image_uuid}")
async def img_preference(
        image_uuid: uuid.UUID,
        body: bodies.ImgPreferenceBody
) ->reses.ImgPreferenceRes:
    image_data = collection.find_one({"uuid": image_uuid.__str__()})

    if image_data is None:
        raise err.ErrorIds.IMAGE_NOT_FOUND.to_exception("image data not found")
    filename = image_data.get("original_filename")
    collection.update_one(
        {"uuid": image_uuid.__str__()},
        {"$set": {"state": body.state.value}}
    )
    return reses.ImgPreferenceRes.create(filename)


@app.get("/preference/{image_uuid}")
async def img_preference(
        image_uuid: uuid.UUID,
) ->reses.ImgPreferenceRes:
    image_data = collection.find_one({"uuid": image_uuid.__str__()})

    if image_data is None:
        raise err.ErrorIds.IMAGE_NOT_FOUND.to_exception("image data not found")
    filename = image_data.get("original_filename")

    return reses.ImgPreferenceRes.create(filename)


@app.get("/img/{image_uuid}/{filename}")
async def get_image(
        image_uuid: str, filename: str | None = None,
        q: Union[str, None] = Query(default=None, max_length=50)
):
    image_uuid = image_uuid.split(".")[0]
    image_data = collection.find_one({"uuid": image_uuid})

    if image_data is None:
        raise HTTPException(status_code=404, detail="Image not found")

    image_state = image_data['state']

    if image_state == 'Public':
        return _stream_image(image_data)

    elif image_state == 'Private':
        if q is None:
            raise HTTPException(status_code=400, detail="Token required")

        token = data.JwtTokenData(**jwt.decode(q, SECRET_KEY, algorithms=[ALGORITHM]))
        if token.token_type == 'Access':
            return _stream_image(image_data)
        else:
            raise HTTPException(status_code=403, detail="Invalid token type")

    return {"status": "Image not Public", "state": image_state}


def _stream_image(image_data):
    file_data = image_data['file_data']
    file_extension = image_data['original_filename'].split('.')[-1]
    file_stream = io.BytesIO(file_data)
    media_type = f"image/{file_extension}"
    return StreamingResponse(file_stream, media_type=media_type)
