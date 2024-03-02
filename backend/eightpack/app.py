import contextlib
import re
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, contains_eager
from starlette.middleware.cors import CORSMiddleware

from eightpack import model
from eightpack import data
from eightpack.config import app_config
from eightpack.core import EngineGlobal, default_get_user, database
from eightpack.util import encrypt_password, validate_password

LOGIN_CHARACTERS = re.compile(r"[A-Za-z0-9_.-]")


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI):
    EngineGlobal.setup(app_config.DB_URL)
    yield
    EngineGlobal.destroy()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users/register")
def register(req: data.RegisterRequest, db: Session = Depends(database)):
    if len(req.login) < 3:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="This username is too short!")
    if not LOGIN_CHARACTERS.match(req.login):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="This username contains invalid characters!"
        )

    user = model.Player(login=req.login, password=encrypt_password(req.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="This username is already used!"
        ) from e
    return data.UserTokenResponse.from_object(user)


@app.post("/users/login")
def login(req: data.LoginRequest, db: Session = Depends(database)):
    query = select(model.Player).where(model.Player.login == req.login)
    result = db.execute(query)
    if not (user := result.scalar()):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="User with this login was not found!")
    if user.virtual:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Logging into this user is not allowed!"
        )
    if not validate_password(req.password, user.password):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Incorrect password!")
    return data.UserTokenResponse.from_object(user)


@app.post("/users/token")
def get_token_info(user: model.Player = Depends(default_get_user)):
    return data.UserInformation.from_object(user)


@app.get("/drafts")
def get_drafts(pagination: data.PaginationRequest = Depends(), db: Session = Depends(database)):
    slice_query, count_query = pagination.convert(
        select(model.Draft)
        .join(model.Draft.front_card)
        .options(contains_eager(model.Draft.front_card))
        .order_by(-model.Draft.id),
        default_page_size=10,
    )
    slice_result, count = db.execute(slice_query), db.execute(count_query).scalar()
    return data.PaginationResponse.from_result(slice_result, count, data.DraftResponse)


@app.get("/drafts/{draft_id}/choices")
def get_draft_choices(draft_id: int, db: Session = Depends(database)):
    query = (
        select(model.DraftOption)
        .where(model.DraftOption.draft_id == draft_id)
        .join(model.DraftOption.card)
        .options(contains_eager(model.DraftOption.card))
    )
    result = db.execute(query)
    return data.DraftChoicesResponse.from_list(result.scalars().all())


@app.post("/drafts/{draft_id}/save")
def save_draft_playthrough(
    draft_id: int,
    choices: data.DraftPlaythroughRequest,
    db: Session = Depends(database),
    user: model.Player = Depends(default_get_user),
):
    picks = [model.DraftPick(turn_number=i, picked_card_id=card) for i, card in enumerate(choices.picks)]
    run = model.DraftRun(player=user, picks=picks, draft_id=draft_id)
    db.add(run)
    db.commit()
    return data.SuccessResponse()


@app.get("/drafts/{draft_id}/playthroughs")
def get_draft_playthroughs(draft_id: int, db: Session = Depends(database)):
    # Due to COUNT DISTINCT we paginate manually
    slice_query = (
        select(model.DraftRun)
        .where(model.DraftRun.draft_id == draft_id)
        .join(model.DraftPick)
        .join(model.Card)
        .order_by(model.DraftRun.id.desc())
        .distinct()
    )
    count_query = select(model.DraftRun).where(model.DraftRun.draft_id == draft_id).with_only_columns(func.count())

    slice_result, count = db.execute(slice_query), db.execute(count_query).scalar()
    return data.PaginationResponse.from_result(slice_result, count, data.DraftPlaythroughResponse)


if __name__ == "__main__":
    uvicorn.run(
        "eightpack.app:app",
        host=app_config.PROJECT_HOST,
        port=app_config.PROJECT_PORT,
        reload=app_config.DEBUG,
    )
