import traceback
import uuid
from datetime import datetime

from bson import Binary
from fastapi import UploadFile, File, Depends
from pydantic import BaseModel
from pymongo import errors

from data import JwtTokenData
from main import app, collection
from tokens import get_token
from util import err


class TokenRes(BaseModel):
    image_uuid: uuid.UUID

    @staticmethod
    def create(image_uuid: uuid.UUID):
        return TokenRes(image_uuid=image_uuid)


@app.post("/upload/")
async def upload_image(
        file: UploadFile = File(...),
        token: JwtTokenData | None = Depends(get_token)
) -> TokenRes:
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

    return TokenRes.create(token.uuid)
