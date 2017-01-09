.PHONY: all
all: test lint

.PHONY: test
test:
	pytest tests.py

.PHONY: doctest
doctest:
	nosetests --with-doctest --doctest-extension=rst

.PHONY: lint
lint:
	flake8 *.py
	pylint --py3k *.py

.PHONY: clean
clean:
	rm -rf *.pyc
	rm -rf *.egg-info
	rm -rf build dist
	rm -rf __pycache__ .tox .cache

.PHONY: format
format:
	isort -a  "from __future__ import absolute_import, print_function, unicode_literals" \
		-rc $(SRC) *.py
	-yapf --style google -r -i $(SRC) *.py
	isort -rc $(SRC) *.py
