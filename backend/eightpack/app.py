import contextlib
import re
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
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
    if len(req.login) < 6:
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
    return data.UserTokenResponse.for_user(user)


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
    return data.UserTokenResponse.for_user(user)


@app.get("/drafts")
def get_drafts(pagination: data.PaginationRequest = Depends(), db: Session = Depends(database)):
    query = pagination.convert(select(model.Draft), default_page_size=10)
    result = db.execute(query)
    return data.PaginationResponse.from_result(result, data.DraftResponse)


@app.get("/drafts/{draft_id}/choices")
def get_draft_choices(draft_id: int, db: Session = Depends(database)):
    query = select(model.DraftOption).where(model.DraftOption.draft_id == draft_id)
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
def get_draft_playthroughs(
    draft_id: int, pagination: data.PaginationRequest = Depends(), db: Session = Depends(database)
):
    query = pagination.convert(
        select(model.DraftRun).where(model.DraftRun.draft.id == draft_id), default_page_size=10
    )
    result = db.execute(query)
    return data.PaginationResponse.from_result(result, data.DraftPlaythroughResponse)


if __name__ == "__main__":
    uvicorn.run(
        "eightpack.app:app",
        host=app_config.PROJECT_HOST,
        port=app_config.PROJECT_PORT,
        reload=app_config.DEBUG,
    )
