# Rust Standards

This directory will contain specifications for Rust-language implementations of the Miri Standard. Nothing here is specified yet — this README sketches the intended scope and the existing Rust machinery each piece will build on.

> Naming note: this project is unrelated to [Miri, the Rust interpreter](https://github.com/rust-lang/miri) used for detecting undefined behavior. The Rust specifications here will acknowledge the collision and may use a qualified prefix (e.g. `miri-standard`) in tooling names to avoid confusion — this is the one ecosystem where the name is already taken.

## Where Rust Starts From

Rust's baseline is strong on tooling and weak on binary legibility:

- **Deprecation is a first-class language attribute.** `#[deprecated(since = "...", note = "...")]` is enforced by the compiler at every call site — the strongest deprecation mechanism in any Miri target ecosystem, and the natural generation source for `migration-guide.json` (the PEP 702 analog; see [Python spec §6](../python/lifecycle-security-metadata.md)).
- **SemVer verification already exists.** [cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks) lints a crate against its previously published API — prior art for the [deprecation coherence checks](../cli/cli-lifecycle-specification.md) and a tool Miri conformance can build on rather than reimplement.
- **Examples are compiled and tested.** rustdoc doc-tests and the `examples/` directory convention mean example code is executable by default.
- **Advisories have a home database.** [RustSec](https://rustsec.org/) feeds OSV; `cargo audit` and `cargo deny` consume it. `cargo yank` handles version withdrawal.
- **But compiled binaries are opaque.** Unlike Go, Rust embeds no dependency manifest in release binaries — a Rust-built CLI needs the SBOM path of the [CLI specification §3](../cli/cli-lifecycle-specification.md) (tools like `cargo auditable`, which embeds the dependency list in a binary section, are the emerging fix and a likely SHOULD).

## Planned Specifications

- **Agent Metadata for Crates** *(Planned)* — an `agent-metadata/` directory in the crate (packaged into the `.crate` tarball), mirroring the [Python agent-metadata specification](../python/agent-metadata-specification.md): `sdk-manifest.json` (generatable from `cargo doc`'s rustdoc JSON output), `usage-patterns.json`, `migration-guide.json` derived from `#[deprecated]` attributes at build time. Configuration via the `[package.metadata.miri]` table in `Cargo.toml`, the sanctioned extension point for third-party tool metadata.
- **Lifecycle Metadata** *(Planned)* — `agent-metadata/lifecycle.json` per the shared schema ([lifecycle-v1.json](../../schemas/lifecycle-v1.json)): identity as `pkg:cargo/<crate>@<version>`, advisory sources (public: RustSec via OSV; private: internal OSV endpoints alongside private/alternate registries), update check via the sparse registry index protocol (crates.io or private registries), and `support` status. Open source vs. private follows the same values-not-structure rule as Python and CLI.
- **Structured Examples** *(Planned)* — binding doc-tests and `examples/` entries to Miri example metadata (complexity, category, learning progression) so they remain compiled and tested by `cargo test`.
- **Rust CLI Conformance Profile** *(Planned)* — how a Rust-built CLI satisfies the [CLI lifecycle specification](../cli/cli-lifecycle-specification.md): `cargo auditable` and/or a CycloneDX SBOM per release for composition (binaries carry no buildinfo), clap integration for per-flag `lifecycle` blocks and `--describe` derived from the same schema-as-data source as `--help`.

## Existing Machinery to Build On

| Concern | Existing Rust mechanism | Miri adds |
|---|---|---|
| Identity | `pkg:cargo/` purl, Cargo.toml | Declaration in lifecycle.json; `cargo auditable` for binaries |
| Vulnerabilities | RustSec (OSV home database), cargo audit/deny | `advisory_sources` declaration for private registries |
| Update state | Sparse registry index, `cargo update --dry-run` | Declared `update_check` endpoint for private registries |
| Examples | Doc-tests, `examples/` directory | Structured metadata: complexity, category, workflow |
| Deprecation | `#[deprecated(since, note)]`, cargo yank | Extraction into migration-guide.json; coherence checks |
| API surface | rustdoc JSON, cargo-semver-checks | sdk-manifest.json generation; agent-oriented indexing |

## Resources

- [The Cargo Book](https://doc.rust-lang.org/cargo/)
- [RustSec Advisory Database](https://rustsec.org/)
- [cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks)
- [cargo auditable](https://github.com/rust-secure-code/cargo-auditable)
- [rustdoc JSON output](https://doc.rust-lang.org/rustdoc/unstable-features.html#-w--output-format-output-format)
- [`[package.metadata]` table](https://doc.rust-lang.org/cargo/reference/manifest.html#the-metadata-table)
