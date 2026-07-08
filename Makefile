# Variables
PYTHON = .env/bin/python
PYTEST = .env/bin/pytest

.PHONY: test snapshot-update clean publish help

help:
	@echo "Available commands:"
	@echo "  make test             Run integration tests"
	@echo "  make snapshot-update  Run tests and update snapshot golden files"
	@echo "  make publish          Build source distribution and upload to PyPI via Twine"
	@echo "  make clean            Remove Python compiled bytecode, distributions, and cache"

test:
	$(PYTEST) -v

snapshot-update:
	$(PYTHON) tests/test_integration.py update

publish:
	@echo "==> Cleaning old distributions..."
	rm -rf dist/*
	@echo "==> Building source distribution..."
	$(PYTHON) setup.py sdist
	@echo "==> Uploading package to PyPI via Twine..."
	$(PYTHON) -m twine upload dist/*

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache dist/ build/ *.egg-info