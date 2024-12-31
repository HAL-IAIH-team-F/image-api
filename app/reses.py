import uuid

from pydantic import BaseModel


class ImgPreferenceRes(BaseModel):
    filename: str

    @staticmethod
    def create(filename: str):
        return ImgPreferenceRes(filename=filename)
