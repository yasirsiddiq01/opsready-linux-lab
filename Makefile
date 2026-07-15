.PHONY: install install-dev run test lint check docker

install:
	python -m pip install -r requirements.txt

install-dev:
	python -m pip install -r requirements-dev.txt

run:
	python -m streamlit run app.py

test:
	python -m pytest -q

lint:
	python -m ruff check .

check: test lint
	python -m compileall -q app.py opsready_lab

docker:
	docker compose up --build
