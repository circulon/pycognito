
.PHONY: install
install:
	pip install ".[dev]"
	pre-commit install

.PHONY: lint
lint: format
	ruff check src tests

.PHONY: format
format:
	ruff format --check src tests

.PHONY: lint-fix
lint-fix:
	ruff check --fix src tests
	ruff format src tests

.PHONY: test
test: lint clean
	tox -e tests

.PHONY: clean
clean:
	rm -rf .tox dist build htmlcov .coverage
