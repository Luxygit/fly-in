
SRC			= main.py
MAP			= maps/easy/01_linear_path.txt
VENV		= .venv
PYTHON		= $(VENV)/bin/python3
PIP			= $(VENV)/bin/pip3

all: install run

install:
	python3 -m venv $(VENV)
	$(PIP) install flake8 mypy

run:
	$(PYTHON) $(SRC) ${MAP}

debug:
	$(PYTHON) -m pdb $(SRC) ${MAP}

clean:
	rm -rf __pycache__ .mypy_cache dist build *.egg-info $(VENV)

lint: install
	$(VENV)/bin/flake8 *.py
	$(VENV)/bin/mypy *.py --warn-return-any --warn-unused-ignores --ignore-missing-import --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	$(VENV)/bin/flake8 *.py
	$(VENV)/bin/mypy *.py --strict

.PHONY: all install run debug clean lint lint-strict
