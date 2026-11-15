"""How each stack is started, and which scenarios it answers."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

BENCH = Path(__file__).resolve().parent.parent
UVICORN_FLAGS = [
    "--loop",
    "uvloop",
    "--http",
    "httptools",
    "--no-access-log",
    "--log-level",
    "warning",
]
PYTHON_SCENARIOS = ("plaintext", "json", "query", "validate", "page", "static")


@dataclass(frozen=True)
class Stack:
    name: str
    what: str
    scenarios: tuple[str, ...]
    cwd: Path = BENCH
    paths: dict[str, str] = field(default_factory=dict)

    def argv(self, port: int, workers: int) -> list[str]:
        raise NotImplementedError

    def path(self, scenario: str, default: str) -> str:
        return self.paths.get(scenario, default)

    def prepare(self) -> list[str] | None:
        """A command to run once before the server starts, if the stack needs one."""
        return None


@dataclass(frozen=True)
class Uvicorn(Stack):
    target: str = ""

    def argv(self, port: int, workers: int) -> list[str]:
        base = [sys.executable, "-m", "uvicorn", self.target, "--port", str(port)]
        return base + ["--workers", str(workers), *UVICORN_FLAGS]


@dataclass(frozen=True)
class Nexy(Stack):
    def argv(self, port: int, workers: int) -> list[str]:
        nexy = str(Path(sys.executable).with_name("nexy"))
        return [nexy, "start", "--port", str(port), "--host", "127.0.0.1"]

    def prepare(self) -> list[str] | None:
        # Without a build, nexy start serves the page without its layout (Nexy 2.3.0).
        return [str(Path(sys.executable).with_name("nexy")), "build"]


@dataclass(frozen=True)
class Reference(Stack):
    def argv(self, port: int, workers: int) -> list[str]:
        binary = BENCH / "reference" / "target" / "release" / "nexy-bench-reference"
        return [str(binary), str(port), str(workers)]


STACKS = (
    Reference("rust", "hyper alone, no Python: the ceiling", ("plaintext", "json")),
    Uvicorn(
        "asgi",
        "a raw ASGI app on uvicorn: the floor of Python",
        PYTHON_SCENARIOS[:4],
        target="apps.asgi_app:app",
    ),
    Uvicorn("starlette", "Starlette on uvicorn", PYTHON_SCENARIOS, target="apps.starlette_app:app"),
    Uvicorn(
        "fastapi",
        "FastAPI on Starlette and uvicorn",
        PYTHON_SCENARIOS,
        target="apps.fastapi_app:app",
    ),
    Nexy(
        "nexy",
        "Nexy as nexy start runs it",
        PYTHON_SCENARIOS,
        cwd=BENCH / "apps" / "nexy_app",
        paths={"static": "/public/asset.txt"},
    ),
)


def by_name(names: list[str] | None) -> list[Stack]:
    """The stacks asked for, in the order of STACKS."""
    if not names:
        return list(STACKS)
    unknown = set(names) - {s.name for s in STACKS}
    if unknown:
        raise ValueError(f"unknown stack: {', '.join(sorted(unknown))}")
    return [s for s in STACKS if s.name in names]
