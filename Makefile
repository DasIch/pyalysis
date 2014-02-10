help:
	@echo "make help     - Shows this text"
	@echo "make dev-env  - Creates development environment"
	@echo "make test     - Runs the tests"
	@echo "make doc      - Build the HTML documentation"
	@echo "make view-doc - View the HTML documentation in your browser"
	@echo "make clean    - Removes all untracked files"

dev-env:
	pip install -r dev-requirements.txt \
		    -r docs/requirements.txt \
		    -r tests/requirements.txt
	pip install -e .

test:
	py.test tests

doc:
	make -C docs html

view-doc: doc
	open docs/_build/html/index.html

clean:
	git ls-files --directory --other | xargs rm -r

.PHONY: help dev-env test doc view-doc clean
