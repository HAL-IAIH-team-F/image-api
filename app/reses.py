import uuid

from pydantic import BaseModel


class TokenRes(BaseModel):
    image_uuid: uuid.UUID

    @staticmethod
    def create(image_uuid: uuid.UUID):
        return TokenRes(image_uuid=image_uuid)