help:
	@echo "make help    - Shows this text"
	@echo "make dev-env - Creates development environment"
	@echo "make test    - Runs the tests"
	@echo "make clean   - Removes all untracked files"

dev-env:
	pip install -r dev-requirements.txt -r test-requirements.txt
	pip install -e .

test:
	py.test tests

clean:
	git ls-files --directory --other | xargs rm -r

.PHONY: help dev-env test clean
