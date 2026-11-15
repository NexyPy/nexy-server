"""Starlette routing and responses on top of uvicorn."""

from __future__ import annotations

from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from apps.common import HERE, PAYLOAD, TEXT, Item, query_row

templates = Jinja2Templates(directory=HERE / "templates")


async def plaintext(request: Request) -> Response:
    return PlainTextResponse(TEXT)


async def payload(request: Request) -> Response:
    return JSONResponse(PAYLOAD)


async def query(request: Request) -> Response:
    return JSONResponse(await run_in_threadpool(query_row))


async def items(request: Request) -> Response:
    item = Item.model_validate_json(await request.body())
    return Response(item.model_dump_json(), media_type="application/json")


async def page(request: Request) -> Response:
    context = {"title": "Bench", "greeting": "Hello Nexy!"}
    return templates.TemplateResponse(request, "page.html", context)


app = Starlette(
    routes=[
        Route("/plaintext", plaintext),
        Route("/payload", payload),
        Route("/query", query),
        Route("/items", items, methods=["POST"]),
        Route("/page", page),
        Mount("/static", StaticFiles(directory=HERE / "static")),
    ]
)
