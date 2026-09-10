# Miri Standard — local development tasks.
# The site is a derived artifact (schema-as-data rule): it is generated, never
# committed. `make site` builds into .generated/site (gitignored) for local
# review; CI publishes the same output to miri-whl/miri-whl.github.io.

OUT := .generated/site
PORT := 8000

.PHONY: help deps envelope consistency references validate validate-sample score-sample site serve clean lint spell links check diagrams

help: ## Show this help
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

deps: ## Install Python dependencies for the site generator
	pip install pyyaml jsonschema jinja2

validate: ## Validate check YAMLs against schemas/check-v2.json (as CI does)
	@python3 -c "\
	import json, pathlib, yaml, jsonschema; \
	schema = json.load(open('schemas/check-v2.json')); \
	jsonschema.Draft7Validator.check_schema(schema); \
	files = sorted(pathlib.Path('standards').glob('*/checks/*.yaml')); \
	[jsonschema.validate(yaml.safe_load(f.read_text()), schema) for f in files]; \
	print(f'{len(files)} check definitions valid')"

validate-sample: ## Validate examples/sample-sdk agent-metadata against the JSON Schemas
	@python3 -c "\
	import json, pathlib, jsonschema; \
	base = pathlib.Path('examples/sample-sdk/src/weather_sdk/agent-metadata'); \
	pairs = [('lifecycle.json','lifecycle-v1'), ('sdk-manifest.json','sdk-manifest-v1'), ('usage-patterns.json','usage-patterns-v1'), ('migration-guide.json','migration-guide-v1'), ('api-graph.json','api-graph-v1')]; \
	[jsonschema.validate(json.load(open(base/f)), json.load(open('schemas/'+s+'.json'))) for f,s in pairs]; \
	print(f'{len(pairs)} sample-sdk metadata files valid')"

score-sample: ## Build examples/sample-sdk and score it with miri (conformance gate; needs miri-py)
	@python3 tools/score_sample.py

fixtures: ## Build the consumption fixtures (bare/miri/adversarial) and verify identical source
	@python3 examples/fixtures/build_fixtures.py

validate-fixtures: fixtures ## Verify the fixture invariants (conforming twin valid; adversarial attacks live)
	@python3 tools/validate_fixtures.py

cli-fixtures: ## Build the greetctl CLI fixture arms (bare/1.0.0/1.1.0/adversarial) and verify one implementation
	@python3 examples/fixtures/cli/build_cli_fixtures.py

validate-cli-fixtures: cli-fixtures ## Verify the CLI fixture invariants (release history exercised; C1-C11 live)
	@python3 tools/validate_cli_fixtures.py

diagrams: ## Render any new/changed ```mermaid fence to a committed SVG (needs npx)
	python3 tools/render_diagrams.py

consistency: ## Catch count/reference/table drift the linters do not see
	python3 tools/check_consistency.py

envelope: ## Validate discovery-envelope-v1.json in both directions (accept + reject)
	python3 tools/validate_envelope_schema.py

findings-schema: ## Validate agent-findings-v1.json in both directions (accept + reject)
	@python3 tools/validate_findings_schema.py

score-cli-linter: ## Prove the CLI golden harness rejects an inert AND a screaming linter
	@python3 tools/score_cli_linter.py --self-test

references: ## Verify every check's spec citations resolve (--report for reconciliation)
	python3 tools/check_references.py

site: validate ## Generate the site into .generated/site for local review
	python3 tools/generate_site.py --out $(OUT)

serve: site ## Generate, then serve at http://localhost:8000
	@echo "Serving at http://localhost:$(PORT)/ (Ctrl-C to stop)"
	python3 -m http.server -d $(OUT) $(PORT)

clean: ## Remove generated site output
	rm -rf .generated site

lint: ## Lint Markdown (CI: markdownlint-cli2)
	# Pinned to the version markdownlint-cli2-action@v16 bundles. Unpinned, npx resolves to a newer
	# release whose added rules (MD060) fail files CI accepts, so `make check` went red on untouched files.
	# Exclusions must be `#`-prefixed globs here: `.markdownlintignore` is a markdownlint-cli v1 file and
	# cli2 does not read it, so its `memory-bank/**` and `.claude/**` entries are inert — both are linted.
	npx -y markdownlint-cli2@0.13 "**/*.md" "#node_modules" "#.generated"

spell: ## Spell-check Markdown (CI: cspell)
	# Pinned for the same reason as `lint`. Note pinning cspell does NOT pin its dictionaries: a real
	# English word can sit in the locally-resolved en_US trie and be absent from the one cspell-action
	# bundles, which passes here and fails CI (this happened with `evaluable`). The version-independent
	# fix for such a word is to add it to `.cspell.json` words, not to rely on either dictionary.
	npx -y cspell@8 --config .cspell.json --no-progress "**/*.md"

links: ## Check Markdown links (CI: markdown-link-check)
	# xargs, not `-exec`: `find -exec` reports find's exit status, so this target printed dead links
	# and still exited 0. xargs exits 123 when any invocation fails, which is what makes `check` red.
	find . -name '*.md' -not -path './node_modules/*' -not -path './.generated/*' -print0 \
		| xargs -0 -n1 npx -y markdown-link-check -q -c .markdown-link-check.json
	# -q prints nothing for a clean file, so a passing run is otherwise silent and reads as "did nothing".
	@echo "links: $$(find . -name '*.md' -not -path './node_modules/*' -not -path './.generated/*' \
		| wc -l | tr -d ' ') file(s), no dead links"

check: validate validate-sample validate-fixtures validate-cli-fixtures findings-schema score-cli-linter lint spell links ## Run everything CI runs locally (except the miri score gate)
