import hashlib
import os
from datetime import timedelta, UTC, datetime
from hmac import compare_digest
from typing import TypeVar

import requests
from jose import jwt
from pydantic import BaseModel

from eightpack import model
from eightpack.config import app_config
from eightpack.data import SignedToken

T = TypeVar("T", bound=BaseModel)


def paginate_scryfall_get(t: type[T], url: str) -> list[T]:
    url = "https://api.scryfall.com" + url
    has_more = True
    items = []
    while has_more:
        data = requests.get(url).json()
        has_more, url = paginate(data, items, t)
    return items


def paginate_scryfall_post(t: type[T], url: str, json: dict) -> list[T]:
    url = "https://api.scryfall.com" + url
    has_more = True
    items = []
    while has_more:
        data = requests.post(url, json=json, headers={"Content-Type": "application/json"}).json()
        has_more, url = paginate(data, items, t)
    return items


def paginate(data: dict, items: list[T], t: type[T]) -> tuple[bool, str]:
    for c in data["data"]:
        items.append(t(**c))
    has_more = data.get("has_more")
    url = data.get("next_page")
    return has_more, url


def remove_face2(name: str) -> str:
    return name.split(" // ")[0]


def encrypt_password(password: str) -> str:
    salt = os.urandom(16)
    algo = "scrypt"
    return hash_password(password, salt, algo)


def hash_password(password: str, salt: bytes, algo: str):
    if algo != "scrypt":
        raise ValueError(f"Unknown cryptographic algorithm: {algo}")
    pass_hash = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return ";".join([algo, salt.hex(), pass_hash.hex()])


def validate_password(pass_hash: str, password: str):
    algo, salt_hex, _ = pass_hash.split(";")
    return compare_digest(pass_hash, hash_password(password, bytes.fromhex(salt_hex), algo))


def sign_token(user: model.Player, duration: timedelta) -> str:
    claims = SignedToken(sub=str(user.id), exp=datetime.now(tz=UTC) + duration)
    return jwt.encode(claims.model_dump(by_alias=True), app_config.JWT_KEY, app_config.JWT_ALGO)


def read_token(token: str) -> SignedToken | None:
    try:
        data = jwt.decode(token, app_config.JWT_KEY, app_config.JWT_ALGO, issuer=app_config.JWT_ISSUER)
    except jwt.JWTError:
        return None

    return SignedToken(**data)
