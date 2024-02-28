from typing import TypeVar

import requests
from pydantic import BaseModel

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
