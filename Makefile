
SRC			= fly_in.py
VENV		= .venv
PYTHON		= $(VENV)/bin/python3
PIP			= $(VENV)/bin/pip3

all: install run

$(VENV):
	python3 -m venv $(VENV)

install: $(VENV)

run:
	$(PYTHON) $(SRC)

debug:
	$(PYTHON) -m $(SRC)

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache dist build *.egg-info

lint:
	flake8 *.py
	mypy *.py --warn-return-any --warn-unused-ignores --ignore-missing-import --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 *.py
	mypy *.py --strict

.PHONY: all install run debug clean lint lint-strict
