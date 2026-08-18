# Go Standards

This directory will contain specifications for Go-language implementations of the Miri Standard. Nothing here is
specified yet — this README sketches the intended scope and the existing Go machinery each piece will build on.

## Why Go Is Different

Go starts from a stronger baseline than any other ecosystem Miri targets:

- **Binaries are already self-identifying.** The toolchain embeds the full module list and versions into every binary,
  readable via `go version -m` — the existence proof behind the
  [CLI specification's](../cli/cli-lifecycle-specification.md) identity requirements.
  [govulncheck](https://go.dev/blog/govulncheck) and osv-scanner already join this against the
  [Go vulnerability database](https://vuln.go.dev/) (an OSV home database).
- **Distribution is source-based.** Modules are fetched as source through the module proxy — so Miri metadata ships as
  ordinary files in the module; there is no wheel-style binary format to extend.
- **Examples are already a tested convention.** `Example*` functions in `_test.go` files are compiled, executed, and
  rendered on pkg.go.dev — a stronger foundation than Python's untested README snippets.
- **Deprecation has a machine-recognizable convention.** The `// Deprecated:` doc comment is understood by pkg.go.dev,
  gopls, and staticcheck; `retract` directives in `go.mod` handle version withdrawal (the yank equivalent).

Miri's job in Go is therefore less about creating machinery and more about **structuring what exists into
agent-consumable form**.

## Planned Specifications

- **Agent Metadata for Go Modules** *(Planned)* — an `agent-metadata/` directory in the module root, mirroring the
  [Python agent-metadata specification](../python/agent-metadata-specification.md): `sdk-manifest.json` (API index —
  generatable from `go/ast` / `go doc -json`), `usage-patterns.json`, and `migration-guide.json`. Generation source for
  deprecations: the `// Deprecated:` comment convention, extracted at build time (the PEP 702 analog — see
  [Python spec §6](../python/lifecycle-security-metadata.md)).
- **Lifecycle Metadata** *(Planned)* — `agent-metadata/lifecycle.json` per the shared schema
  ([lifecycle-v1.json](../../schemas/lifecycle-v1.json)): identity as `pkg:golang/<module>@<version>`, advisory sources
  (public: Go vulndb via OSV; private: internal OSV endpoints and `GOPRIVATE`/`GONOSUMCHECK` module patterns), update
  check via the module proxy `@latest` endpoint (public or private `GOPROXY`), and `support` status. Open source vs.
  private follows the same values-not-structure rule as Python and CLI.
- **Structured Examples** *(Planned)* — conventions binding `Example*` functions to Miri example metadata (complexity,
  category, learning progression) rather than inventing a parallel example store; examples stay compiled and tested by
  `go test`.
- **Go CLI Conformance Profile** *(Planned)* — how a Go-built CLI satisfies the
  [CLI lifecycle specification](../cli/cli-lifecycle-specification.md) with minimal extra work:
  `identity.build_info.embedded_modules: true` from debug.ReadBuildInfo, SBOM optional when buildinfo is intact,
  cobra/flag integration for per-flag `lifecycle` blocks and `--describe`.

## Existing Machinery to Build On

| Concern | Existing Go mechanism | Miri adds |
|---|---|---|
| Identity | Embedded buildinfo, `pkg:golang/` purl | Declaration in lifecycle.json; private-module conventions |
| Vulnerabilities | Go vulndb (OSV home database), govulncheck | `advisory_sources` declaration for private modules |
| Update state | Module proxy `@latest`, `go list -m -u` | Declared `update_check` endpoint for private proxies |
| Examples | Testable `Example*` functions, pkg.go.dev | Structured metadata: complexity, category, workflow |
| Deprecation | `// Deprecated:` comments, staticcheck, `retract` | Extraction into migration-guide.json; coherence checks |
| API surface | `go doc -json`, `go/ast`, apidiff | sdk-manifest.json generation; agent-oriented indexing |

## Resources

- [Go Modules Reference](https://go.dev/ref/mod)
- [Go Vulnerability Management](https://go.dev/security/vuln/)
- [govulncheck](https://go.dev/blog/govulncheck)
- [Testable Examples in Go](https://go.dev/blog/examples)
- [Go module proxy protocol](https://go.dev/ref/mod#goproxy-protocol)
