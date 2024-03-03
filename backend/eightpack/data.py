import abc
from datetime import datetime, timedelta
from typing import TypeVar, Generic, Any, Collection

from pydantic import BaseModel
from slugify import slugify
from sqlalchemy import Select, Result, func

from eightpack import model
from eightpack.util import sign_token


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
    layout: str

    def to_model(self) -> model.Card:
        return model.Card(
            name=self.name,
            image=self.image_uris.normal,
            art_image=self.image_uris.art_crop,
            slug=slugify(self.name),
            rarity=self.rarity,
            layout=self.layout,
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
    page_size: int | None = None

    def convert(
        self, query: Select, *, default_page_size: int = 10, max_page_size: int = 50
    ) -> tuple[Select, Select]:
        page_size = min(max_page_size, self.page_size or default_page_size)
        slice_q = query.slice(page_size * self.page_num, page_size * (self.page_num + 1))
        count_q = query.order_by(None).with_only_columns(func.count())
        return slice_q, count_q


class PaginationResponse(BaseModel, Generic[T]):
    total_objects: int
    data: list[T]

    @classmethod
    def from_result(cls, result: Result, count: int, t: type[T]) -> "PaginationResponse[T]":
        return PaginationResponse(
            total_objects=count, data=[t.from_object(o) for o in result.scalars().all()]
        )


class DraftPlaythroughRequest(BaseModel):
    # This is the easiest way to make sure there are exactly 8 picks in the playthrough
    picks: tuple[int, int, int, int, int, int, int, int]


class SuccessResponse(BaseModel):
    success: bool = True


class UserTokenResponse(BaseModel):
    success: bool = True
    token: str

    @classmethod
    def from_object(cls, user: model.Player) -> "UserTokenResponse":
        return cls(token=sign_token(user, timedelta(days=14)))


class UserInformation(BaseModel):
    login: str
    id: int

    @classmethod
    def from_object(cls, user: model.Player) -> "UserInformation":
        return cls(login=user.name, id=user.id)


class CardResponse(BaseModel):
    id: int
    name: str
    image: str
    art_image: str
    slug: str

    @classmethod
    def from_object(cls, obj: model.Card):
        return cls(id=obj.id, name=obj.name, image=obj.image, art_image=obj.art_image, slug=obj.slug)


class DraftResponse(FromObjectModel):
    id: int
    date: datetime
    front_card: CardResponse
    run_count: int
    player_name: str

    @classmethod
    def from_object(cls, obj: model.Draft):
        return cls(
            front_card=CardResponse.from_object(obj.front_card),
            id=obj.id,
            date=obj.created_at,
            run_count=obj.run_count,
            player_name=obj.first_player.name,
        )


class DraftPlaythroughResponse(FromObjectModel):
    id: int
    player_id: int
    player_name: str
    created_at: datetime
    is_og: bool
    cards: list[CardResponse]

    @classmethod
    def from_object(cls, obj: model.DraftRun):
        return cls(
            id=obj.id,
            player_id=obj.player_id,
            player_name=obj.player.name,
            created_at=obj.created_at,
            is_og=obj.is_original,
            cards=[CardResponse.from_object(p.picked_card) for p in obj.draft_picks],
        )


class ManyDraftPlaythroughsResponse(BaseModel):
    playthroughs: list[DraftPlaythroughResponse]

    @classmethod
    def from_list(cls, items: Collection[model.DraftRun]):
        return cls(playthroughs=[DraftPlaythroughResponse.from_object(obj) for obj in items])


class DraftChoicesResponse(BaseModel):
    cards: list[list[CardResponse]]

    @classmethod
    def from_list(cls, items: Collection[model.DraftOption]):
        cards_per_turn = [[] for _ in range(8)]
        for item in items:
            cards_per_turn[item.turn_number].append(CardResponse.from_object(item.card))
        return cls(cards=cards_per_turn)
