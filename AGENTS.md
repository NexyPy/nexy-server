# nexy-server - Agent Guide

## Scope

The HTTP server and API layer of Nexy, written in Rust. It replaces uvicorn, Starlette and FastAPI under Nexy without changing the code a developer writes. It stays a module of Nexy, not an independent framework. The API is designed in the
issues before any implementation.

## Order of work

1. Read the issue, the README and the official documentation of every tool involved. Check
   current versions and advisories with the registries, not from memory.
2. Verify the research by running a command that answers the question. A claim without a
   command is not a fact.
3. Write the test that fails, write the least code that passes, then refactor.
4. Run every gate and quote what it printed. A gate that was not run does not exist.

## Branches

- `main` is the release branch. It receives reviewed changes from `develop` and release commits.
- `develop` is the integration branch. Work branches start from `develop` and target `develop`.
- Work branches use `feature/*`, `fix/*`, `docs/*` and `perf/*`, named after the issue.
- Only the maintainer merges into `main` and `develop`. A contributor works on a branch and waits
  for the review.
- Branch protection requires a pull request, one code owner approval, an approval after the last
  push, up-to-date branches and every CI check. Force pushes and deletion are refused.

## Code and characters

- Code, comments, identifiers, docs, issues, pull requests and commits are in English.
- Use only characters typed on an English or French keyboard. No emoji, no smart punctuation.
- No AI tool appears as an author or co-author. No bot account commits here.

## Gates

Run these commands from the root before a commit.

```bash
python3 scripts/check_attribution.py --range origin/develop..HEAD
python3 scripts/check_human_characters.py
python3 scripts/check_release_setup.py --publish-command 'cargo publish --locked'
```

Run the full gate set from the root before a commit.

```bash
python3 scripts/verify.py
```

This runs `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`,
`cargo test --all-targets --locked`, `cargo build --release --locked`, the character check, the
release setup check and the commit attribution check. The dependency audit and the crate packaging
run in CI against the frozen lock.

## Releases

Publishing is prepared but dormant. The design phase has no package to publish yet. The external
registry setup is recorded in `docs/release-setup.md`.
