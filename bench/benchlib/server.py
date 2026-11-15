"""Start a stack, wait until it answers, sample its memory, stop it."""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Self

from benchlib.memory import tree_rss_mib
from benchlib.stacks import BENCH, Stack


def environment(workers: int) -> dict[str, str]:
    """The apps import `apps.common`; Nexy reads its worker count from BENCH_WORKERS."""
    return {**os.environ, "PYTHONPATH": str(BENCH), "BENCH_WORKERS": str(workers)}


def wait_ready(url: str, timeout: float = 30.0) -> None:
    """Return once *url* answers; fail loudly after *timeout* seconds."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1).read()
            return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"server did not answer {url} within {timeout:.0f}s")


@contextmanager
def started(stack: Stack, port: int, workers: int, prefix: list[str]) -> Iterator[int]:
    """The stack listening on *port*, pinned by *prefix*; yields the pid of its main process."""
    argv = prefix + stack.argv(port, workers)
    if stack.prepare():
        subprocess.run(
            stack.prepare(),
            cwd=stack.cwd,
            env=environment(workers),
            check=True,
            stdout=subprocess.DEVNULL,
        )
    process = subprocess.Popen(
        argv,
        cwd=stack.cwd,
        env=environment(workers),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        wait_ready(f"http://127.0.0.1:{port}/plaintext")
        yield process.pid
    finally:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=30)


class PeakMemory:
    """Samples the memory of a process tree in the background and keeps the highest value."""

    def __init__(self, pid: int, every: float = 0.25) -> None:
        self.pid, self.every, self.peak = pid, every, 0.0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)

    def _sample(self) -> None:
        while not self._stop.is_set():
            self.peak = max(self.peak, tree_rss_mib(self.pid))
            self._stop.wait(self.every)

    def __enter__(self) -> Self:
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        self._thread.join()
