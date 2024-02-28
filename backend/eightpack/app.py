import contextlib

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from eightpack.config import app_config
from eightpack.core import EngineGlobal


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
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users/register")
def register():
    pass


@app.post("/users/login")
def login():
    pass


@app.get("/drafts")
def get_drafts():
    pass


@app.get("/drafts/{draft_id}/choices")
def get_draft_choices(draft_id: int):
    pass


@app.post("/drafts/{draft_id}/save")
def save_draft_playthrough(draft_id: int):
    pass


@app.get("/drafts/{draft_id}/playthroughs")
def get_draft_playthroughs(draft_id: int):
    pass


if __name__ == "__main__":
    uvicorn.run(
        "eightpack.app:app",
        host=app_config.PROJECT_HOST,
        port=app_config.PROJECT_PORT,
        reload=app_config.DEBUG,
    )
