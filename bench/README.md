# Benchmarks

The baseline of Nexy as it runs today, and the ceiling of the machine it runs on. Every change in
nexy-server is measured here against these numbers, on the same machine, with the same settings.

## What is measured

Five stacks answer the same requests, from the barest to the full framework, so the cost of each
layer shows as the difference between two lines:

| Stack | What runs |
|---|---|
| `rust` | hyper alone, no Python: the ceiling of the machine |
| `asgi` | a raw ASGI app on uvicorn: the floor of a Python server |
| `starlette` | Starlette routing and responses on uvicorn |
| `fastapi` | FastAPI on Starlette and uvicorn |
| `nexy` | a Nexy project, built with `nexy build` and served by `nexy start` |

| Scenario | Request |
|---|---|
| `plaintext` | `GET /plaintext`, 13 bytes of text: the cost of the server itself |
| `json` | `GET /payload`, a small dict encoded as JSON |
| `query` | `GET /query`, one SQLite row by a random id |
| `validate` | `POST /items`, a JSON body validated by Pydantic and sent back |
| `page` | `GET /page`, an HTML page with a layout, rendered per request |
| `static` | `GET /static/asset.txt` (`/public/asset.txt` in Nexy), a 4 KB file |

For each pair the runner keeps the requests per second, the p50 and p99 latency, the errors, and
the resident memory of the server and all its workers, idle and at its peak under load.

## Rules

- The server and the load generator run on separate cores (`taskset`), so they do not steal time
  from each other. By default the server gets two thirds of the cores and one worker per core.
- Every stack gets the same cores and the same worker count.
- Each scenario has an unmeasured warm-up, then runs `--repeat` times (3 by default) with a
  cool-down pause before each run; the run with the median requests per second is kept.
- The hottest CPU temperature is written with the results: a laptop that throttles gives numbers
  that only compare with numbers taken in the same state.
- The versions of every package, the CPU and the kernel are written at the top of each result.
- A result is only compared with results from the same machine.

## Run

```bash
cargo install oha --locked                       # the load generator
cargo build --release --manifest-path reference/Cargo.toml
uv sync
uv run python run.py                             # every stack, every scenario
uv run python run.py --stacks nexy fastapi --scenarios json --seconds 20
```

Results go to `results/<date>-<label>.md` and `.json`. Linux only: memory is read from `/proc`.

## Tests

```bash
PYTHONPATH=. uv run pytest
```
