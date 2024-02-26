server:
	python3 -m http.server -d public

install:
	poetry install

pytest: install
	poetry run pytest --cov=topmatchnba tests

run: install
	poetry run topmatchnba
