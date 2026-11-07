PYTHON ?= $(if $(wildcard pipeline/.venv/bin/python),pipeline/.venv/bin/python,python3)
PNPM ?= pnpm
ARGS ?=

.PHONY: data extract model export sync check dev

data:
	$(PYTHON) -m pipeline.ingest.download $(ARGS)
	$(PYTHON) -m pipeline.ingest.build_terms $(ARGS)
	$(PYTHON) -m pipeline.ingest.build_panel $(ARGS)

extract:
	$(PYTHON) -m pipeline.extract.run_batch $(ARGS)

model:
	$(PYTHON) -m pipeline.model.outcomes $(ARGS)
	$(PYTHON) -m pipeline.model.backtest $(ARGS)
	$(PYTHON) -m pipeline.model.pca_map $(ARGS)

export:
	$(PYTHON) -m pipeline.model.export $(ARGS)
	$(PYTHON) scripts/contracts.py

sync:
	$(PYTHON) scripts/contracts.py --sync

check: sync
	$(PYTHON) scripts/contracts.py
	$(PYTHON) -m ruff check pipeline scripts
	$(PYTHON) -m pytest -q
	$(PYTHON) scripts/check_ownership.py
	cd app && $(PNPM) typecheck && $(PNPM) lint && $(PNPM) test

dev:
	cd app && $(PNPM) dev
