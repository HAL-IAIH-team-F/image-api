import io
from typing import Union

from fastapi import Query, HTTPException, Depends
from jose import jwt
from starlette.responses import StreamingResponse

import data
from env import SECRET_KEY, ALGORITHM
from main import app, collection


class __Service:
    def __init__(
            self,
            image_uuid: str, filename: str | None = None,
            q: Union[str, None] = Query(default=None, max_length=1024),
            download: Union[bool, None] = Query(default=False),
    ):
        self.__image_uuid = image_uuid
        self.__filename = filename
        self.__q = q
        self.__download = download

    def process(self):
        image_uuid = self.__image_uuid.split(".")[0]
        image_data = collection.find_one({"uuid": image_uuid})

        if image_data is None:
            raise HTTPException(status_code=404, detail="Image not found")

        image_state = image_data['state']

        if image_state == 'Public':
            return self.__stream_image(image_data)

        if image_state != 'Private':
            return {"status": "Image not Public", "state": image_state}
        if self.__q is None:
            raise HTTPException(status_code=400, detail="Token required")

        token = data.JwtTokenData(**jwt.decode(self.__q, SECRET_KEY, algorithms=[ALGORITHM]))

        if str(token.file_uuid) != image_uuid:
            raise HTTPException(status_code=403, detail="Invalid token")
        if token.token_type == 'Access':
            return self.__stream_image(image_data)

        raise HTTPException(status_code=403, detail="Invalid token type")

    def __stream_image(self, image_data: dict):
        file_data = image_data['file_data']
        file_extension = image_data['original_filename'].split('.')[-1]
        file_stream = io.BytesIO(file_data)
        if "content_type" in image_data.keys():
            content_type = image_data['content_type']
        else:
            content_type = f"image/{file_extension}"
        headers = dict[str, str]()
        if self.__download:
            headers["Content-Disposition"] = f"attachment; filename={image_data['original_filename']}"
        else:
            headers["Content-Disposition"] = f"inline; filename={image_data['original_filename']}"
        return StreamingResponse(
            file_stream, media_type=content_type, headers=headers
        )


@app.get("/img/{image_uuid}/{filename}")
async def get_image(
        service: __Service = Depends()
):
    return service.process()
