"""Resident memory of a server and all its workers, read from /proc (Linux)."""

from __future__ import annotations

from pathlib import Path

PROC = Path("/proc")


def children(pid: int) -> list[int]:
    """The direct children of a process."""
    found: list[int] = []
    for task in (PROC / str(pid) / "task").glob("*"):
        text = (task / "children").read_text() if (task / "children").exists() else ""
        found += [int(child) for child in text.split()]
    return found


def tree(pid: int) -> list[int]:
    """A process and every process below it."""
    pids, todo = [], [pid]
    while todo:
        current = todo.pop()
        pids.append(current)
        todo += children(current)
    return pids


def rss_kib(pid: int) -> int:
    """Resident memory of one process, 0 when it is gone."""
    try:
        status = (PROC / str(pid) / "status").read_text()
    except OSError:
        return 0
    for line in status.splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1])
    return 0


def tree_rss_mib(pid: int) -> float:
    """Resident memory of a server and its workers, in MiB."""
    return sum(rss_kib(p) for p in tree(pid)) / 1024
