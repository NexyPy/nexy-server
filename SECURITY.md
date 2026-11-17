# Security policy

## Reporting a vulnerability

Open a private security advisory on this repository. Include the affected version, the steps to
reproduce the issue and the impact. Do not open a public issue for an unfixed vulnerability.

## What is checked

- `cargo clippy --all-targets -- -D warnings` runs on every push.
- `cargo audit` runs against the frozen lock on every push.
- Dependabot opens weekly updates for Cargo and GitHub Actions.
- Every hostile input gets a test that asserts the refusal.
- Releases are packaged and verified before upload, then published with crates.io Trusted
  Publishing.
- The publish job has only `id-token: write` and never shares a process with the verify job.

## Accepted risks

None today. An accepted risk is a finding that cannot be fixed, with a one-line justification next
to the code and an entry here. An entry expires when the dependency or the code changes.

## Dependency audit register

No advisory is ignored. An ignore would need a dated reason here and a test that proves the
exposure does not apply to this crate.
