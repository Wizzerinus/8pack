from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


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
