.PHONY: pre-commit dev test dist check clean

pre-commit:
	pre-commit run --all-files

dev:
	pip install -q -e .

test: clean
	tox

dist:
	python setup.py sdist bdist_wheel

check:
	python setup.py check

clean:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete
