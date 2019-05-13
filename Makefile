.PHONY: pre-commit dev test dist check test-upload clean

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

test-upload:
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

clean:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete
