"""The results as JSON for machines and as a Markdown table for people."""

from __future__ import annotations

from typing import Any

HEADER = (
    "| Stack | Scenario | Requests/s | p50 ms | p99 ms | Errors | RSS idle MiB | RSS peak MiB |"
)
RULE = "|---|---|---:|---:|---:|---:|---:|---:|"


def error_count(row: dict[str, Any]) -> int:
    """Responses that are not 2xx, plus requests that got no response."""
    bad = sum(n for code, n in row["statuses"].items() if not code.startswith("2"))
    return bad + row["failures"]


def line(row: dict[str, Any]) -> str:
    cells = [
        row["stack"],
        row["scenario"],
        f"{row['rps']:,.0f}",
        f"{row['p50_ms']:.2f}",
        f"{row['p99_ms']:.2f}",
        str(error_count(row)),
        f"{row['rss_idle_mib']:.0f}",
        f"{row['rss_peak_mib']:.0f}",
    ]
    return "| " + " | ".join(cells) + " |"


def markdown(meta: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    """A self-contained page: the machine, the settings, then one line per measure."""
    head = [f"# Baseline, {meta['date']}", ""]
    head += [f"- **{key}**: {value}" for key, value in meta.items() if key != "date"]
    return "\n".join(head + ["", HEADER, RULE] + [line(row) for row in rows]) + "\n"
