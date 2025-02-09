import io
from typing import Union

from fastapi import HTTPException
from fastapi import Query
from fastapi.responses import StreamingResponse

from main import app, collection
from tokens import *


@app.get("/img/{image_uuid}/{filename}")
async def get_image(
        image_uuid: str, filename: str | None = None,
        q: Union[str, None] = Query(default=None, max_length=1024)
):
    image_uuid = image_uuid.split(".")[0]
    image_data = collection.find_one({"uuid": image_uuid})

    if image_data is None:
        raise HTTPException(status_code=404, detail="Image not found")

    image_state = image_data['state']

    if image_state == 'Public':
        return _stream_image(image_data)

    if image_state != 'Private':
        return {"status": "Image not Public", "state": image_state}
    if q is None:
        raise HTTPException(status_code=400, detail="Token required")

    token = data.JwtTokenData(**jwt.decode(q, SECRET_KEY, algorithms=[ALGORITHM]))
    if token.file_uuid != image_uuid:
        raise HTTPException(status_code=403, detail="Invalid token")
    if token.token_type == 'Access':
        return _stream_image(image_data)

    raise HTTPException(status_code=403, detail="Invalid token type")


def _stream_image(image_data: dict):
    file_data = image_data['file_data']
    file_extension = image_data['original_filename'].split('.')[-1]
    file_stream = io.BytesIO(file_data)
    if "content_type" in image_data.keys():
        content_type = image_data['content_type']
    else:
        content_type = f"image/{file_extension}"
    return StreamingResponse(file_stream, media_type=content_type)
