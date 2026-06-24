from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from pathlib import Path

import fastapi_chameleon

from routers import (
    motecture,
    handlers,
)


# establish app with no docs
app = FastAPI(docs_url=None, redoc_url=None)

app.exception_handler(404)(handlers.not_found_error)
app.exception_handler(500)(handlers.internal_error)

BASE_DIR = Path(__file__).resolve().parent
template_folder = str(BASE_DIR / "templates")
fastapi_chameleon.global_init(template_folder)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/content-assets", StaticFiles(directory="content"), name="content-assets")

app.include_router(motecture.router)
