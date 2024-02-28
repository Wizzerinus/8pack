import abc
from datetime import datetime
from typing import TypeVar, Generic, Any, Collection

from pydantic import BaseModel, Field
from slugify import slugify
from sqlalchemy import Select, Result

from eightpack import model
from eightpack.config import app_config


class SignedToken(BaseModel):
    issuer: str = Field(alias="iss", default=app_config.JWT_ISSUER, init_var=False)
    user_id: str = Field(alias="sub", default=...)
    expiry_date: datetime = Field(alias="exp", default=...)


class FromObjectModel(BaseModel, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_object(cls: "type[T]", obj: Any) -> "T":
        pass


T = TypeVar("T", bound=FromObjectModel)


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

    def to_model(self) -> model.Card:
        return model.Card(
            name=self.name,
            image=self.image_uris.normal,
            art_image=self.image_uris.art_crop,
            slug=slugify(self.name),
            rarity=self.rarity,
            set=self.set,
        )


class RegisterRequest(BaseModel):
    login: str
    password: str


class LoginRequest(BaseModel):
    login: str
    password: str


class PaginationRequest(BaseModel):
    page_num: int = 0
    page_size: int = None

    def convert(self, query: Select, *, default_page_size: int = 10, max_page_size: int = 50) -> Select:
        # TODO
        pass


class PaginationResponse(BaseModel, Generic[T]):
    total_objects: int
    data: list[T]

    @classmethod
    def from_result(cls, result: Result, t: type[T]) -> "PaginationResponse[T]":
        # TODO
        pass


class DraftPlaythroughRequest(BaseModel):
    # This is the easiest way to make sure there are exactly 8 picks in the playthrough
    picks: tuple[int, int, int, int, int, int, int, int]


class SuccessResponse(BaseModel):
    success: bool = True


class UserTokenResponse(BaseModel):
    success: bool = True
    token: str

    @classmethod
    def from_user(cls, user: model.Player) -> "UserTokenResponse":
        # TODO
        pass


class DraftResponse(FromObjectModel):
    @classmethod
    def from_object(cls, obj: model.Draft):
        # TODO
        return cls()


class DraftPlaythroughResponse(FromObjectModel):
    @classmethod
    def from_object(cls, obj: model.DraftRun):
        # TODO
        return cls()


class DraftChoicesResponse(BaseModel):
    @classmethod
    def from_list(cls, items: Collection[model.DraftOption]):
        # TODO
        pass
