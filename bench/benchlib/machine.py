"""What the results depend on: the machine, the interpreter, the versions."""

from __future__ import annotations

import os
import platform
from datetime import date
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PACKAGES = ("nexy", "fastapi", "starlette", "uvicorn", "pydantic", "uvloop", "httptools")


def cpu_model() -> str:
    for text in Path("/proc/cpuinfo").read_text().splitlines():
        if text.startswith("model name"):
            return text.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def hottest() -> str:
    """The hottest thermal zone: a laptop that throttles gives numbers that do not compare."""
    temps = [int(p.read_text()) for p in Path("/sys/class/thermal").glob("thermal_zone*/temp")]
    return f"{max(temps) / 1000:.0f} C" if temps else "unknown"


def package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "absent"


def describe(settings: dict[str, object]) -> dict[str, object]:
    """The header of a result file."""
    versions = ", ".join(f"{name} {package_version(name)}" for name in PACKAGES)
    return {
        "date": date.today().isoformat(),
        "cpu": f"{cpu_model()}, {os.cpu_count()} logical cores",
        "system": f"{platform.system()} {platform.release()}",
        "python": f"{platform.python_implementation()} {platform.python_version()}",
        "versions": versions,
        **settings,
    }
