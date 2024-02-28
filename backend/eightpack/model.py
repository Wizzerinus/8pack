from sqlalchemy import inspect, ForeignKey, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    def __repr__(self):
        fields_arr = [f"addr={id(self)}"]
        fields_arr.extend(f"{k}={getattr(self, k, None)}" for k in inspect(self.__class__).columns.keys())
        fields = ", ".join(fields_arr)
        return f"{self.__class__.__name__}({fields})"


class DraftPick(Base):
    __tablename__ = "draft_picks"
    id: Mapped[int] = mapped_column(primary_key=True)
    draft_run_id: Mapped[int] = mapped_column(ForeignKey("draft_runs.id"))
    turn_number: Mapped[int] = mapped_column()
    picked_card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    picked_card: Mapped["Card"] = relationship()


class DraftOption(Base):
    __tablename__ = "draft_options"
    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("drafts.id"))
    turn_number: Mapped[int] = mapped_column()
    option_number: Mapped[int] = mapped_column()
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    card: Mapped["Card"] = relationship()

    __table_args__ = (UniqueConstraint("turn_number", "option_number", "draft_id"), )


class DraftRun(Base):
    __tablename__ = "draft_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("drafts.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    player: Mapped["Player"] = relationship()
    draft_picks: Mapped[list[DraftPick]] = relationship()


class Draft(Base):
    __tablename__ = "drafts"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[int] = mapped_column(DateTime(), server_default=func.now(), onupdate=func.now())
    draft_runs: Mapped[list[DraftRun]] = relationship()
    draft_options: Mapped[list[DraftOption]] = relationship()


class Card(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    image: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(50))

    __table_args__ = (UniqueConstraint("slug"), )


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(128))
    virtual: Mapped[bool] = mapped_column(default=False)
