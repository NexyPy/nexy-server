"""Run every local quality gate in order, stopping at the first failure.

Usage: python3 scripts/verify.py
The network audit stays in CI; every other gate runs here.
"""

import argparse
import subprocess
import sys

RUST_GATES: list[tuple[str, list[str]]] = [
    ("format", ["cargo", "fmt", "--all", "--", "--check"]),
    ("lint", ["cargo", "clippy", "--all-targets", "--locked", "--", "-D", "warnings"]),
    ("test", ["cargo", "test", "--all-targets", "--locked"]),
    ("build", ["cargo", "build", "--release", "--locked"]),
]

PYTHON_GATES: list[tuple[str, list[str]]] = [
    ("characters", ["scripts/check_human_characters.py"]),
    (
        "release",
        [
            "scripts/check_release_setup.py",
            "--publish-command",
            "cargo publish --locked",
        ],
    ),
]


def run(name: str, command: list[str]) -> int:
    print(f"[verify] {name}: {' '.join(command)}")
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print(f"[verify] FAILED at {name}")
        return result.returncode
    print(f"[verify] {name}: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/develop")
    parser.parse_args(argv)
    for name, command in RUST_GATES:
        if run(name, command) != 0:
            return 1
    for name, args in PYTHON_GATES:
        if run(name, [sys.executable, *args]) != 0:
            return 1
    if run(
        "attribution",
        [sys.executable, "scripts/check_attribution.py", "--range", "origin/develop..HEAD"],
    ) != 0:
        return 1
    print("[verify] all gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
