# Release Room. Run `make help` for targets.
SHELL := /bin/bash
.DEFAULT_GOAL := help

DEMO_APP_REPO ?= https://github.com/bhanu-dev82/release-room-demo-app.git
REVIEWS_CSV   ?= data/reviews.synthetic.csv
FIXER_DIR     := workspace/fixer/release-room-demo-app
REVIEWER_DIR  := workspace/reviewer/release-room-demo-app

.PHONY: help setup sample triage replies test demo-data reset check

help: ## List targets
	@grep -hE '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  %-10s %s\n", $$1, $$2}'

setup: ## Install Python dependencies (needs uv)
	uv sync

sample: ## Regenerate the synthetic review set (fixed seed)
	uv run python -m tools.make_sample --out data/reviews.synthetic.csv

triage: ## Reviews -> ranked cards in data/out/cards.md
	uv run python -m tools.triage --csv $(REVIEWS_CSV)

replies: ## Reply drafts: make replies CARD=CARD-1 VERSION=1.4.2 SUMMARY="..."
	@test -n "$(CARD)" -a -n "$(VERSION)" -a -n "$(SUMMARY)" || { echo 'usage: make replies CARD=CARD-1 VERSION=1.4.2 SUMMARY="what is fixed"'; exit 2; }
	uv run python -m tools.replies --card "$(CARD)" --version "$(VERSION)" --summary "$(SUMMARY)"

test: ## Run the test suite
	uv run pytest -q

demo-data: ## Give the fixer and reviewer their own clones of the demo app
	@if [ -e workspace ]; then echo "workspace/ already exists. Run 'make reset' to rebuild it."; exit 1; fi
	git clone -q $(DEMO_APP_REPO) $(FIXER_DIR)
	git clone -q $(DEMO_APP_REPO) $(REVIEWER_DIR)
	cp agents/fixer/opencode.json $(FIXER_DIR)/opencode.json
	cp agents/reviewer/opencode.json $(REVIEWER_DIR)/opencode.json
	echo opencode.json >> $(FIXER_DIR)/.git/info/exclude
	echo opencode.json >> $(REVIEWER_DIR)/.git/info/exclude
	git -C $(REVIEWER_DIR) remote add fixer ../../fixer/release-room-demo-app
	@echo "Agent clones ready in workspace/ (fixer can push; reviewer is read-only)."

reset: ## Delete workspace/ (including unpushed agent work) and rebuild it
	rm -rf workspace
	$(MAKE) demo-data

check: ## Pre-push checks: tests pass, no secrets tracked
	uv run pytest -q
	@if git grep -nE '(sk-[A-Za-z0-9]{16}|xai-[A-Za-z0-9]{16}|AIza[0-9A-Za-z_-]{20}|-----BEGIN|[MN][A-Za-z0-9]{23}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27})' -- . ':!Makefile'; then echo "Possible secret above. Remove it before pushing."; exit 1; fi
	@echo "check passed"
