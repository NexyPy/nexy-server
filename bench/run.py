"""Measure every stack on every scenario and write the results.

uv run python run.py                       # everything, defaults below
uv run python run.py --stacks nexy fastapi --scenarios plaintext json
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import time
from dataclasses import asdict
from pathlib import Path

from apps.common import create_db
from benchlib import load, machine, report, scenarios, stacks
from benchlib.memory import tree_rss_mib
from benchlib.server import PeakMemory, started

RESULTS = Path(__file__).parent / "results"


def options() -> argparse.Namespace:
    cores = os.cpu_count() or 2
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stacks", nargs="*", help="default: all")
    parser.add_argument("--scenarios", nargs="*", help="default: all")
    parser.add_argument("--seconds", type=int, default=10, help="measured time per scenario")
    parser.add_argument("--warmup", type=int, default=3, help="unmeasured time before it")
    parser.add_argument("--repeat", type=int, default=3, help="runs per scenario, median kept")
    parser.add_argument("--pause", type=int, default=3, help="cool-down seconds between runs")
    parser.add_argument("--connections", type=int, default=64)
    parser.add_argument("--server-cpus", default=f"0-{max(cores * 2 // 3 - 1, 0)}")
    parser.add_argument("--client-cpus", default=f"{cores * 2 // 3}-{cores - 1}")
    parser.add_argument("--label", default=socket.gethostname())
    return parser.parse_args()


def cpu_count(cpus: str) -> int:
    """How many cores a taskset list such as 0-3 or 0,2,4 names."""
    total = 0
    for part in cpus.split(","):
        low, _, high = part.partition("-")
        total += int(high or low) - int(low) + 1
    return total


def median_run(argv: list[str], client: list[str], args) -> load.Measure:
    """The run with the median requests per second, a pause before each one."""
    runs = []
    for _ in range(args.repeat):
        time.sleep(args.pause)
        runs.append(load.run(argv, client))
    return sorted(runs, key=lambda run: run.rps)[len(runs) // 2]


def measure(stack, scenario, args, pid: int, port: int) -> dict:
    url = f"http://127.0.0.1:{port}{stack.path(scenario.name, scenario.path)}"
    client = ["taskset", "-c", args.client_cpus]
    load.run(load.oha_argv(url, scenario, args.warmup, args.connections), client)
    idle = tree_rss_mib(pid)
    with PeakMemory(pid) as memory:
        argv = load.oha_argv(url, scenario, args.seconds, args.connections)
        result = median_run(argv, client, args)
    row = {"stack": stack.name, "scenario": scenario.name, **asdict(result)}
    return {**row, "rss_idle_mib": idle, "rss_peak_mib": memory.peak}


def run_stack(stack, chosen, args, port: int) -> list[dict]:
    workers = cpu_count(args.server_cpus)
    wanted = [s for s in chosen if s.name in stack.scenarios]
    with started(stack, port, workers, ["taskset", "-c", args.server_cpus]) as pid:
        time.sleep(1)
        return [measure(stack, scenario, args, pid, port) for scenario in wanted]


def save(meta: dict, rows: list[dict]) -> Path:
    RESULTS.mkdir(exist_ok=True)
    stem = RESULTS / f"{meta['date']}-{meta['label']}"
    stem.with_suffix(".json").write_text(json.dumps({"meta": meta, "rows": rows}, indent=2) + "\n")
    stem.with_suffix(".md").write_text(report.markdown(meta, rows))
    return stem.with_suffix(".md")


def main() -> None:
    args = options()
    create_db()
    settings = {
        "label": args.label,
        "server cpus": args.server_cpus,
        "client cpus": args.client_cpus,
        "connections": args.connections,
        "seconds": args.seconds,
        "workers": cpu_count(args.server_cpus),
    }
    rows: list[dict] = []
    for offset, stack in enumerate(stacks.by_name(args.stacks)):
        rows += run_stack(stack, scenarios.by_name(args.scenarios), args, 8100 + offset)
        print(f"{stack.name}: done")
    meta = {**machine.describe(settings), "hottest cpu after the run": machine.hottest()}
    print(save(meta, rows).read_text())


if __name__ == "__main__":
    main()
