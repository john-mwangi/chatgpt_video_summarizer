"""This module handles API authentication. It requires a user to log in with
a valid username and password in order to obtain an JWT access token."""

import os
import re
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from video_summarizer.backend.configs.config import ApiSettings
from video_summarizer.backend.utils.utils import logger

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = ApiSettings.load_settings().algorithm
TOKEN_EXPIRY = ApiSettings.load_settings().access_token_expire_minutes
API_PREFIX = ApiSettings.load_settings().api_prefix

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/token")
secret_key = APIKeyHeader(name="Authorization", scheme_name="Bearer")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"Authorization": "Bearer"},
)

apikey_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=f"Invalid API key provided",
)

# TODO: use Firebase
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "api_keys": {"f7099f6f0f4caa6cf63b88e8d3e7", "a6cf63b88e8d3e7"},
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: dict, username: str):
    if username in db.keys():
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(
    username: str, password: str, fake_db: dict = fake_users_db
):
    user = get_user(fake_db, username)
    if not user:
        logger.info(f"{username=} does not exist")
        return False
    if not verify_password(password, user.hashed_password):
        logger.info(f"{username=} provided an incorrect password")
        return False
    return user


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=TOKEN_EXPIRY),
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"{encoded_jwt=}")
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def validate_api_key(api_key: Annotated[str, Depends(secret_key)]):
    # Swagger UI will accept any key but the validation happens server-side
    matches = re.match(pattern=r"Bearer\s(.*)", string=api_key)

    if matches is None:
        logger.info("No API key was provided")
        raise apikey_exception

    elif matches[1] not in fake_users_db.get("api_keys"):
        logger.info(f"Invalid API key: {matches[1}")
        raise apikey_exception

    else:
        return True


if __name__ == "__main__":
    import requests

    hashed_password1 = pwd_context.hash(secret="secret")
    hashed_password2 = (
        "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )

    is_valid1 = pwd_context.verify("secret", hashed_password1)
    is_valid2 = pwd_context.verify("secret", hashed_password2)

    print(hashed_password1, hashed_password2)
    print(is_valid1, is_valid2)

    headers_success = {"Authorization": "Bearer f7099f6f0f4caa6cf63b88e8d3e7"}
    headers_fail = {"Authorization": "Bearer inexistent_key"}

    resp_success = requests.get(
        url="http://0.0.0.0:12000/api/v1/items?something=value_to_return",
        headers=headers_success,
    )

    resp_fail = requests.get(
        url="http://0.0.0.0:12000/api/v1/items?something=value_to_return",
        headers=headers_fail,
    )

    assert resp_success.status_code == status.HTTP_200_OK
    assert resp_fail.status_code == status.HTTP_403_FORBIDDEN
