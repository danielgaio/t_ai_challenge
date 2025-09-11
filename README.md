# t_ai_challenge

# t_ai — running tests

This folder contains a small test suite for the package dispatcher. Below are the recommended steps to create a virtual environment, install test dependencies, and run the tests on macOS (zsh).

Quick checklist
- Create a virtual environment
- Activate it
- Install `pytest` (recommended)
- Run the tests from the repository root

Recommended commands (zsh)

1) Create and activate a virtual environment

```bash
python3 -m venv env
source env/bin/activate
```

2) Upgrade pip and install pytest

```bash
pip install --upgrade pip
pip install pytest
```

3) Run the tests (from the repository root)

```bash
# run with pytest (preferred)
pytest -q

# or run a single file
pytest -q tests/test_package_dispatcher.py
```

Alternative (no pytest required)

```bash
# Run the tests using the builtin unittest discovery from the repository root
python -m unittest discover -v tests
```

Notes
- Be sure you run the commands from the project root so the `t_ai` package/folder is importable.
- If you see import errors, verify your current working directory and that the virtual environment is active.
