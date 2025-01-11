from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JwtTokenData(BaseModel):
    exp: datetime
    token_type: str
    file_uuid: UUID

    @staticmethod
    def from_args(uuid: UUID, exp: datetime, token_type: str, ):
        return JwtTokenData(file_uuid=uuid, exp=exp, token_type=token_type)


class TokenData(BaseModel):
    token: str
    expires_in: datetime

    @staticmethod
    def from_args(token: str, expires_in: datetime) -> 'TokenData':
        return TokenData(token=token, expires_in=expires_in)


class TokensRes(BaseModel):
    access_token: TokenData
    refresh_token: TokenData

    @staticmethod
    def from_args(access_token: TokenData, refresh_token: TokenData):
        return TokensRes(access_token=access_token, refresh_token=refresh_token)
