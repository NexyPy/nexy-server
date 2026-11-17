//! The version imported by users is the version the build publishes.

use nexy_server::VERSION;

const MANIFEST: &str = include_str!("../Cargo.toml");

#[test]
fn version_matches_package_manifest() {
    assert!(MANIFEST.contains(&format!("version = \"{VERSION}\"")));
}
