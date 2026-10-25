# lotto

A new Python project.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
lotto
# or
python -m lotto.main
```

## Test

```bash
pytest
```

## Layout

```
lotto/
├── pyproject.toml
├── README.md
├── src/lotto/
│   ├── __init__.py
│   └── main.py
└── tests/
    └── test_main.py
```
