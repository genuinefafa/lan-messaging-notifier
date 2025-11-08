# Setup Guide

## First Time Setup

After cloning this repository, you'll need to generate the `poetry.lock` file:

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Generate lock file
poetry lock

# Install dependencies
poetry install
```

## Why poetry.lock is not committed

The `poetry.lock` file is intentionally not included in the initial commit. It should be generated on first setup using `poetry lock`. This ensures:

1. Compatibility with your system and Python version
2. Latest compatible versions of all dependencies
3. No conflicts between different development environments

## After First Setup

Once you run `poetry lock` and `poetry install`, you should commit the generated `poetry.lock` file:

```bash
git add poetry.lock
git commit -m "Add poetry.lock after initial setup"
```

This will ensure all developers use the exact same dependency versions.

## Quick Start Commands

```bash
# 1. Generate lock file
poetry lock

# 2. Install all dependencies
poetry install

# 3. Copy and configure environment
cp .env.example .env
# Edit .env with your API credentials

# 4. Run the application
poetry run python -m src.app

# 5. Run tests
poetry run pytest
```

## Development Workflow

```bash
# Activate virtual environment
poetry shell

# Run application
python -m src.app

# Run tests
pytest

# Format code
black src/ tests/

# Type check
mypy src/
```
