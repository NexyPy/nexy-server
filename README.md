# nexy-server

The HTTP server and API layer of Nexy, written in Rust. It replaces uvicorn, Starlette and FastAPI
under Nexy without changing the code a developer writes: the same files, the same handlers, the
same `Depends`, the same Pydantic models, the same `/docs`. Only the speed and the memory use
change.

## The contract

1. An app that runs on Nexy today runs on nexy-server with no code change.
2. A route, a handler, a dependency or a model written in the FastAPI style keeps its behaviour,
   including validation errors and the OpenAPI document.
3. The switch is one setting in `nexyconfig.py` until it becomes the default, and the ASGI stack
   stays available as a fallback until then.

## Architecture

| Layer | Replaces | Approach |
|---|---|---|
| Network I/O | uvicorn, uvloop, httptools | Rust, one event loop per core, `SO_REUSEPORT`, io_uring on Linux where available, HTTP/1.1 with pipelining, HTTP/2, WebSocket |
| Responses with no Python | Starlette static files | static files, SSG pages and cached responses served by Rust alone, never entering the interpreter |
| Routing and parsing | Starlette routing | radix tree router, headers, query, cookies and multipart parsed in Rust |
| Validation and JSON | FastAPI on Pydantic | schemas compiled once at startup on pydantic-core (already Rust), JSON encoded in Rust |
| Python execution | worker processes | chosen automatically: parallel threads on free-threaded CPython (3.14t), one subinterpreter per core on standard CPython, processes as the last resort |
| Compatibility | FastAPI, Starlette | an API layer with the FastAPI names, and an ASGI bridge so existing middleware keeps working |

Parallelism is automatic: the server reads the core count, the memory available and the
interpreter build, and sizes itself. A developer sets nothing.

## Performance goals

The ambition is to reach the throughput of the fastest Rust and C++ servers (actix-web, may-minihttp,
drogon) while using less memory than the current Python stack. The long-term target set for Nexy is
more than 15 million requests and connections per second.

For scale: the best results of the TechEmpower benchmarks are around 7 million requests per second,
on large multi-core servers, for the plaintext test with HTTP pipelining. A request that runs a
Python handler costs far more than that test. So the goals are tracked per path:

- paths served by Rust alone (static, SSG, cache): measured against actix-web and drogon;
- paths that run Python: measured against uvicorn with FastAPI, Granian and Robyn;
- memory: resident memory per worker, idle and under load.

Every release publishes these numbers, on the same machine, with the scripts in this repository.
No figure is claimed before it is measured.

## Roadmap

1. Benchmark harness and the baseline of Nexy today (uvicorn, Starlette, FastAPI).
2. Rust HTTP core with the ASGI bridge: Nexy runs unchanged, without uvicorn.
3. Responses with no Python served from Rust: static files, SSG pages, cache.
4. Rust router and request parsing: the Nexy routers target it directly, without Starlette.
5. The FastAPI-compatible API layer: dependencies, validation, OpenAPI, without FastAPI.
6. Parallel Python: free-threaded CPython and subinterpreters.
7. Opt-in setting in Nexy, then the default.

## Status

Design phase. Nothing is published yet.

## License

MIT
