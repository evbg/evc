.PHONY: pre-commit dev test dist check clean

pre-commit:
	pre-commit run --all-files

dev:
	pip install -q -e .

test: clean
	tox

dist:
	tox -c tox_dist.ini

check:
	python3 -m twine check dist/*

clean:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete
