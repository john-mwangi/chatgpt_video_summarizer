import os
from datetime import datetime, timedelta, timezone

import yaml
from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel

from video_summarizer.backend.configs import configs

with open(configs.params_path, mode="r") as f:
    params = yaml.safe_load(f)["endpoint"]

ALGORITHM = params["algorithm"]
ACCESS_TOKEN_EXPIRE_MINUTES = params["access_token_expire_minutes"]
SECRET_KEY = os.environ["SECRET_KEY"]


class Token(BaseModel):
    token: str
    token_type: type


class TokenData(BaseModel):
    username: str


def create_access_token(data: dict, expires_min: int):
    """Generate a token for a username"""

    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_min)
    to_encode.update({"exp": expire})
    jwt_encoded = jwt.encode(
        claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM
    )

    return jwt_encoded


def get_current_user(token):
    """Authenticate a username based on a token"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
        user_name = payload.get("sub")
        if user_name is None:
            raise credentials_exception
        token_data = TokenData(username=user_name)
    except JWTError:
        raise credentials_exception

    return token_data.username
