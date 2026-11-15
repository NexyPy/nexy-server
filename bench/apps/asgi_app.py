"""The floor: a raw ASGI app, so the cost measured is uvicorn's own."""

from __future__ import annotations

import json

from apps.common import PAYLOAD, TEXT, Item, query_row

TEXT_HEADERS = [(b"content-type", b"text/plain")]
JSON_HEADERS = [(b"content-type", b"application/json")]


async def _send(send, status: int, headers, body: bytes) -> None:
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})


async def _read(receive) -> bytes:
    body, more = b"", True
    while more:
        message = await receive()
        body += message.get("body", b"")
        more = message.get("more_body", False)
    return body


async def _answer(path: str, receive) -> tuple[int, list, bytes]:
    if path == "/plaintext":
        return 200, TEXT_HEADERS, TEXT
    if path == "/payload":
        return 200, JSON_HEADERS, json.dumps(PAYLOAD).encode()
    if path == "/query":
        return 200, JSON_HEADERS, json.dumps(query_row()).encode()
    if path == "/items":
        item = Item.model_validate_json(await _read(receive))
        return 200, JSON_HEADERS, item.model_dump_json().encode()
    return 404, TEXT_HEADERS, b"Not Found"


async def app(scope, receive, send) -> None:
    if scope["type"] != "http":
        return
    status, headers, body = await _answer(scope["path"], receive)
    await _send(send, status, headers, body)
