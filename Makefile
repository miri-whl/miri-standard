# Miri Standard — local development tasks.
# The site is a derived artifact (schema-as-data rule): it is generated, never
# committed. `make site` builds into .generated/site (gitignored) for local
# review; CI publishes the same output to miri-whl/miri-whl.github.io.

OUT := .generated/site
PORT := 8000

.PHONY: help deps validate validate-sample score-sample site serve clean lint spell links check

help: ## Show this help
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

deps: ## Install Python dependencies for the site generator
	pip install pyyaml jsonschema jinja2

validate: ## Validate check YAMLs against schemas/check-v1.json (as CI does)
	@python3 -c "\
	import json, pathlib, yaml, jsonschema; \
	schema = json.load(open('schemas/check-v1.json')); \
	jsonschema.Draft7Validator.check_schema(schema); \
	files = sorted(pathlib.Path('standards').glob('*/checks/*.yaml')); \
	[jsonschema.validate(yaml.safe_load(f.read_text()), schema) for f in files]; \
	print(f'{len(files)} check definitions valid')"

validate-sample: ## Validate examples/sample-sdk agent-metadata against the JSON Schemas
	@python3 -c "\
	import json, pathlib, jsonschema; \
	base = pathlib.Path('examples/sample-sdk/src/weather_sdk/agent-metadata'); \
	pairs = [('lifecycle.json','lifecycle-v1'), ('sdk-manifest.json','sdk-manifest-v1'), ('usage-patterns.json','usage-patterns-v1'), ('migration-guide.json','migration-guide-v1')]; \
	[jsonschema.validate(json.load(open(base/f)), json.load(open('schemas/'+s+'.json'))) for f,s in pairs]; \
	print(f'{len(pairs)} sample-sdk metadata files valid')"

score-sample: ## Build examples/sample-sdk and score it with miri (conformance gate; needs miri-py)
	@python3 tools/score_sample.py

site: validate ## Generate the site into .generated/site for local review
	python3 tools/generate_site.py --out $(OUT)

serve: site ## Generate, then serve at http://localhost:8000
	@echo "Serving at http://localhost:$(PORT)/ (Ctrl-C to stop)"
	python3 -m http.server -d $(OUT) $(PORT)

clean: ## Remove generated site output
	rm -rf .generated site

lint: ## Lint Markdown (CI: markdownlint-cli2)
	npx markdownlint-cli2 "**/*.md" "#node_modules"

spell: ## Spell-check Markdown (CI: cspell)
	npx cspell --config .cspell.json --no-progress "**/*.md"

links: ## Check Markdown links (CI: markdown-link-check)
	find . -name '*.md' -not -path './node_modules/*' -not -path './.generated/*' \
		-exec npx markdown-link-check -q -c .markdown-link-check.json {} \;

check: validate validate-sample lint spell ## Run everything CI runs locally (except link check and the miri score gate)
