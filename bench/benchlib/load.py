"""Load generation with oha, and the numbers kept from its report."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass

from benchlib.scenarios import Scenario


@dataclass(frozen=True)
class Measure:
    rps: float
    p50_ms: float
    p99_ms: float
    success: float
    statuses: dict[str, int]
    failures: int


def oha_binary() -> str:
    """The oha on PATH, or a clear error that says how to get it."""
    found = shutil.which("oha")
    if not found:
        raise SystemExit("oha is missing: cargo install oha --locked")
    return found


def oha_argv(url: str, scenario: Scenario, seconds: int, connections: int) -> list[str]:
    """The oha command for one scenario, JSON report on stdout."""
    argv = [oha_binary(), "-z", f"{seconds}s", "-c", str(connections), "--no-tui"]
    argv += ["--output-format", "json", "-m", scenario.method]
    if scenario.body is not None:
        argv += ["-d", scenario.body, "-T", "application/json"]
    return argv + [url]


# Requests still in flight when the measured time ends: cut by oha, not refused by the server.
CUT_AT_DEADLINE = "aborted due to deadline"


def failures(errors: dict[str, int]) -> int:
    """Requests that got no response, not counting the ones cut at the deadline."""
    return sum(int(n) for kind, n in errors.items() if kind != CUT_AT_DEADLINE)


def parse(report: dict) -> Measure:
    """The numbers kept from an oha JSON report; latencies come in seconds."""
    summary, percentiles = report["summary"], report["latencyPercentiles"]
    return Measure(
        rps=float(summary["requestsPerSec"]),
        p50_ms=float(percentiles["p50"] or 0) * 1000,
        p99_ms=float(percentiles["p99"] or 0) * 1000,
        success=float(summary["successRate"]),
        statuses={str(k): int(v) for k, v in report.get("statusCodeDistribution", {}).items()},
        failures=failures(report.get("errorDistribution", {})),
    )


def run(argv: list[str], prefix: list[str]) -> Measure:
    """Run oha, pinned by *prefix* (taskset), and parse its report."""
    out = subprocess.run(prefix + argv, capture_output=True, text=True, check=True).stdout
    return parse(json.loads(out))
