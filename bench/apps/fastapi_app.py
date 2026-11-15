"""FastAPI on top of Starlette and uvicorn, written the way its docs show."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from apps.common import HERE, PAYLOAD, TEXT, Item, query_row

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
templates = Jinja2Templates(directory=HERE / "templates")
app.mount("/static", StaticFiles(directory=HERE / "static"))


@app.get("/plaintext", response_class=PlainTextResponse)
async def plaintext() -> bytes:
    return TEXT


@app.get("/payload")
async def payload() -> dict[str, str]:
    return PAYLOAD


@app.get("/query")
def query() -> dict[str, int]:
    return query_row()


@app.post("/items")
async def items(item: Item) -> Item:
    return item


@app.get("/page", response_class=HTMLResponse)
async def page(request: Request) -> HTMLResponse:
    context = {"title": "Bench", "greeting": "Hello Nexy!"}
    return templates.TemplateResponse(request, "page.html", context)
