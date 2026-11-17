# Release setup for nexy-server

This repository is in design phase. The release workflow is prepared but no release is published
yet. This page records the external setup needed for the first release to crates.io.

## What is in the repository

- `.github/workflows/release.yml` verifies the crate and publishes it when a version tag is pushed
  to `main`.
- The verify and publish jobs are separate. The publish job has only `id-token: write` and uses the
  `crates-io` GitHub environment.
- No long-lived API token is stored in the repository.

## Setup on crates.io

1. Publish the crate once from a local machine with an API token. Trusted publishing can only be
   configured on a crate that already exists. This is the only long-lived token in the process.
2. Open the crate Settings, then Trusted Publishing, then Add, and select GitHub.
3. Use these values:
   - Repository owner: `NexyPy`
   - Repository name: `nexy-server`
   - Workflow filename: `release.yml`
   - Environment: `crates-io`
4. Remove the local API token after the first publish. Later releases use the OIDC token.

## Setup on GitHub

1. Create an environment named `crates-io` in the repository settings. Add required reviewers if
   the maintainer wants a manual gate before publishing.
2. Tag a commit already on `main` with `v<major>.<minor>.<patch>` and push the tag.

## What happens on a tag

1. The build job checks that the commit is on `main`, that the tag matches the crate version, then
   runs `cargo check` and `cargo test`.
2. The publish job exchanges the GitHub OIDC token for a short-lived crates.io token with
   `rust-lang/crates-io-auth-action` and runs `cargo publish --locked`.
3. The release job creates the GitHub release from the tag.

## Sources

- https://crates.io/docs/trusted-publishing/
- https://github.com/rust-lang/crates-io-auth-action
