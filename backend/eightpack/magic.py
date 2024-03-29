import csv
import dataclasses
import gzip
import itertools
import os
from typing import IO
from urllib.parse import urlencode

import requests

from eightpack.core import EngineGlobal
from eightpack.data import FormatData, ScryfallCard
from eightpack import model
from eightpack.util import paginate_scryfall_get, paginate_scryfall_post, remove_face2

# We're currently only supporting one format
FORMAT = FormatData(name="Murders at Karlov Manor", set_code="MKM", picks_per_pack=13)
SPECIAL_SETS = ["spg", "plst"]
# don't show these card layouts on front page because they have a stupid art crop
BAD_LAYOUTS = ["split", "flip", "class", "case", "saga", "battle"]

# draft filename aliases because they're long
DRAFT_FILENAMES = {
    "local-premier": "../draft_data_public.MKM.PremierDraft.csv.gz",
    "local-traditional": "../draft_data_public.MKM.TradDraft.csv.gz",
    "17lands-premier": "https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.MKM.PremierDraft.csv.gz",
    "17lands-traditional": "https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.MKM.TradDraft.csv.gz",
}


@dataclasses.dataclass
class DraftParseResponse:
    item: model.Draft | None = None
    skip_lines: int = 0


def fetch_cards(expansion: str) -> list[model.Card]:
    cards = []
    set_query = urlencode({"q": f"set:{expansion}"})
    for card in paginate_scryfall_get(ScryfallCard, f"/cards/search?{set_query}"):
        cards.append(card.to_model())
    return cards


# I don't know of a good way to fetch cards from THE LIST that belong to a given set
# But actually, 17-lands gives us the list of such cards
def fetch_the_list(names: list[str]) -> list[model.Card]:
    assert len(names) <= 75, f"Didn't expect this many The List cards: {len(names)}"
    cards = []
    for card in itertools.chain.from_iterable(
        [
            paginate_scryfall_post(
                ScryfallCard,
                "/cards/collection",
                {"identifiers": [{"name": remove_face2(n), "set": set_name} for n in names]},
            )
            for set_name in SPECIAL_SETS
        ]
    ):
        cards.append(card.to_model())
    return cards


class DraftParser:
    def __init__(self, fmt: FormatData, player: model.Player, cards: list[model.Card]):
        self.format = fmt
        self.player = player
        self.thelist_cards: list[model.Card] = []
        self.cards: dict[str, model.Card] = {}
        self.add_cards(cards)

    def add_cards(self, cards: list[model.Card]):
        for c in cards:
            self.cards[c.name] = c
            self.cards[remove_face2(c.name)] = c

    @classmethod
    def parse_gzip(cls, file_name: str, user: model.Player, cards: list[model.Card]):
        c = cls(FORMAT, user, cards)
        file_name = DRAFT_FILENAMES.get(file_name, file_name)
        should_delete_file = False
        if file_name.startswith("http://") or file_name.startswith("https://"):
            gzip_url = file_name
            file_name = file_name.rsplit("/", 1)[1]
            req = requests.get(gzip_url).content
            with open(file_name, "wb") as f:
                f.write(req)
            should_delete_file = True
        with gzip.open(file_name, "rt", newline="") as f:
            output = c.parse_csv(f)

        if should_delete_file:
            os.remove(file_name)
        return output + c.thelist_cards

    @staticmethod
    def get_cards_from_row(row: dict[str, str]) -> list[str]:
        cards = []
        for k, v in row.items():
            if k.startswith("pack_card_"):
                card_name = k[10:]
                for i in range(int(v)):
                    cards.append(card_name)
        return cards

    def make_draft(self, rows: list[dict[str, str]]) -> DraftParseResponse:
        if rows[0]["expansion"] != FORMAT.set_code:
            return DraftParseResponse()
        if len({r["draft_id"] for r in rows}) != 1:
            last_draft_count = sum(x["draft_id"] == rows[-1]["draft_id"] for x in rows)
            skips = len(rows) - last_draft_count
            return DraftParseResponse(skip_lines=skips)

        rows = rows[:8]
        row_cards = []
        picks = []
        for r in rows:
            picks.append(self.cards[r["pick"]])
            row_cards.append([self.cards[c] for c in self.get_cards_from_row(r)])
        front_card = max(
            [c for c in row_cards[0] if c.layout not in BAD_LAYOUTS],
            key=lambda c: (
                ["common", "uncommon", "rare", "mythic"].index(c.rarity),
                c.set not in SPECIAL_SETS,
            ),
        )

        draft_options = []
        draft_picks = []
        for i, r in enumerate(row_cards):
            for j, c in enumerate(r):
                draft_options.append(model.DraftOption(turn_number=i, option_number=j, card=c))
            draft_picks.append(model.DraftPick(turn_number=i, picked_card=picks[i]))

        run = model.DraftRun(player=self.player, draft_picks=draft_picks, is_original=True)
        return DraftParseResponse(
            item=model.Draft(
                draft_options=draft_options, draft_runs=[run], front_card=front_card, first_player=self.player
            )
        )

    def parse_csv(self, contents: IO[str]) -> list[model.Draft]:
        # We're only extracting a small number of drafts from the CSV to not clog the database
        # because the CSV file is actually 4 gb in size even for new formats (MKM)
        # We also assume that all drafts are different because the chance for even the first
        # pack (15 cards) to repeat is negligibly low
        draft_duration = self.format.picks_per_pack * 3
        already_extracted = []

        reader = csv.DictReader(contents)
        # the list, lmao.
        all_cards = [x[10:] for x in reader.fieldnames if x.startswith("pack_card_")]
        thelist_card_names = [c for c in all_cards if c not in self.cards]
        self.thelist_cards = fetch_the_list(thelist_card_names)
        self.add_cards(self.thelist_cards)
        try:
            for i in range(25):
                rows = [next(reader) for _ in range(draft_duration)]
                draft = self.make_draft(rows)
                if draft.item:
                    already_extracted.append(draft.item)
                if draft.skip_lines:
                    for _ in range(draft.skip_lines):
                        next(reader)
        except StopIteration:  # we have less than 25 drafts wtf
            pass

        return already_extracted


def do_imports(db_url: str, lands_file_name: str):
    EngineGlobal.setup(db_url)
    db = EngineGlobal.DBConnection()
    user = model.Player(login="$17lands", name="a 17lands user", password="", virtual=True)
    cards = fetch_cards(FORMAT.set_code.lower())
    drafts = DraftParser.parse_gzip(lands_file_name, user, cards)  # also includes The List cards

    db.add(user)
    db.add_all(cards)
    db.add_all(drafts)

    with EngineGlobal.engine.begin() as conn:
        model.Base.metadata.drop_all(conn)
        model.Base.metadata.create_all(conn)
    db.commit()
    EngineGlobal.destroy()
