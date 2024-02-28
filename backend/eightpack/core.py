from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy import Engine, create_engine, select, Select
from sqlalchemy.orm import Session, sessionmaker
from starlette.requests import Request

from eightpack import model
from eightpack.util import read_token, SignedToken


class EngineGlobal:
    engine: Engine | None = None
    DBConnection: sessionmaker[Session] | None = None

    @classmethod
    def setup(cls, url: str, *, expire_on_commit: bool = False) -> None:
        if cls.engine is not None:
            raise RuntimeError("Duplicate setup of EngineGlobal!")

        cls.engine = create_engine(url)
        cls.DBConnection = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.engine, expire_on_commit=expire_on_commit
        )

    @classmethod
    def destroy(cls) -> None:
        if cls.engine is None:
            raise RuntimeError("No EngineGlobal to destroy!")

        cls.engine.dispose()
        cls.engine = cls.DBConnection = None


def database(url: str | None = None):
    if url is not None:
        EngineGlobal.setup(url)

    if EngineGlobal.engine is None or EngineGlobal.DBConnection is None:
        raise RuntimeError("EngineGlobal is not initialized!")

    db = EngineGlobal.DBConnection()
    try:
        yield db
    finally:
        db.close()


def get_access_token(request: Request) -> SignedToken | None:
    scheme, _, auth = request.headers.get("Authorization", "").partition(" ")
    if scheme != "Bearer":
        return None
    return read_token(auth)


def requires_login(token: SignedToken | None = Depends(get_access_token)) -> SignedToken:
    if not token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid access token!")
    return token


class GetUser:
    def __init__(self, query: Select[tuple[model.Player]] | None = None):
        self.query = query if query is not None else select(model.Player)

    def __call__(self, db: Session = Depends(database), token: SignedToken = Depends(requires_login)):
        if token is None:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid access token!")

        result = db.execute(self.query.where(model.Player.id == int(token.user_id)))
        if user := result.scalar():
            return user

        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="User not found!")


default_get_user = GetUser()
