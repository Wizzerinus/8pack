from pydantic import BaseModel


class FormatData(BaseModel):
    name: str
    set_code: str
    picks_per_pack: int = 15


class ScryfallImageURLs(BaseModel):
    png: str


class ScryfallCard(BaseModel):
    name: str
    image_uris: ScryfallImageURLs
