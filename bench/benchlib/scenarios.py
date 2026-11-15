"""The requests every stack is measured on."""

from __future__ import annotations

from dataclasses import dataclass

ITEM_BODY = '{"name": "keyboard", "price": 49.9, "tags": ["usb", "mechanical"]}'


@dataclass(frozen=True)
class Scenario:
    name: str
    path: str
    method: str = "GET"
    body: str | None = None
    what: str = ""


SCENARIOS = (
    Scenario("plaintext", "/plaintext", what="13 bytes of text, the cost of the server itself"),
    Scenario("json", "/payload", what="a small dict encoded as JSON"),
    Scenario("query", "/query", what="one SQLite row by a random id"),
    Scenario("validate", "/items", "POST", ITEM_BODY, what="a JSON body validated by Pydantic"),
    Scenario("page", "/page", what="an HTML page with a layout, rendered per request"),
    Scenario("static", "/static/asset.txt", what="a 4 KB file from disk"),
)


def by_name(names: list[str] | None) -> list[Scenario]:
    """The scenarios asked for, in the order of SCENARIOS."""
    if not names:
        return list(SCENARIOS)
    unknown = set(names) - {s.name for s in SCENARIOS}
    if unknown:
        raise ValueError(f"unknown scenario: {', '.join(sorted(unknown))}")
    return [s for s in SCENARIOS if s.name in names]
