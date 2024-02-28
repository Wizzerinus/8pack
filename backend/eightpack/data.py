from pydantic import BaseModel


class FormatData(BaseModel):
    name: str
    set_code: str
    picks_per_pack: int = 15


class ScryfallImageURLs(BaseModel):
    normal: str
    art_crop: str


class ScryfallCard(BaseModel):
    name: str
    image_uris: ScryfallImageURLs
    rarity: str
    set: str
