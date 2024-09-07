from datetime import timedelta, datetime, timezone

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.env import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, REFRESH_TOKEN_EXPIRE_MINUTES
from app import data
from app.data import TokenData, TokensRes
from app.env import SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/refresh", auto_error=False)


def create_token(token_type: str = "Access", expires_delta: timedelta | None = None):
    expire = datetime.now(timezone.utc) + expires_delta
    generated_uuid = str(uuid.uuid4())
    encoded_jwt = jwt.encode(
        data.JwtTokenData.from_args(uuid=generated_uuid,exp=expire,token_type=token_type).model_dump(),
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return TokenData.from_args(encoded_jwt, expire)


def create_upload_token():
    return create_token("Upload", expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))


def create_access_token(user_id: int):
    return create_token(user_id, "Access", timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def get_token_or_none(token: str | None = Depends(oauth2_scheme)):
    if token is None:
        return None
    return data.JwtTokenData(**jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]))


def get_token(token: data.JwtTokenData | None = Depends(get_token_or_none)):
    if token is None:
        raise Exception
    return token


def access_token_or_none(token: data.JwtTokenData | None = Depends(get_token_or_none)):
    if token is None:
        return None
    if token.token_type != "Access":
        raise Exception
    return token
