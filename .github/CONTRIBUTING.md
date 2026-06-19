# Contributing to AgentForge

Thank you for your interest in contributing to AgentForge! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git

### Getting Started

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/<your-username>/agentforge.git
cd agentforge

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Development Workflow

### Branch Naming

- `feature/<description>` — New features
- `fix/<description>` — Bug fixes
- `docs/<description>` — Documentation changes
- `refactor/<description>` — Code refactoring

### Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for linting issues
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/
```

The Ruff configuration is in `pyproject.toml` and targets Python 3.11+.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentforge --cov-report=term-missing

# Run a specific test file
pytest tests/test_cli.py

# Run tests matching a pattern
pytest -k "test_install"
```

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new skill sharing via gist
fix: handle missing config file gracefully
docs: update README with quickstart guide
test: add tests for search command
refactor: simplify registry initialization
```

## Adding a New CLI Command

1. Create a new file in `src/agentforge/cli/` (e.g., `my_cmd.py`)
2. Implement the Click command with Rich output
3. Import and register it in `src/agentforge/cli/main.py`
4. Add tests in `tests/`
5. Update the README if applicable

## Adding a New Skill to the Registry

Skills are defined as YAML files. To add a new skill:

1. Create the skill definition file
2. Add it to the appropriate category directory
3. Submit a PR with a description of the skill

## Submitting Changes

1. Ensure all tests pass: `pytest`
2. Ensure code is lint-clean: `ruff check src/ tests/`
3. Ensure code is formatted: `ruff format --check src/ tests/`
4. Push your branch and open a Pull Request
5. Fill out the PR template with a clear description

## Reporting Issues

- Use the [Bug Report](https://github.com/zzj1965186613/agentforge/issues/new?template=bug_report.md) template for bugs
- Use the [Feature Request](https://github.com/zzj1965186613/agentforge/issues/new?template=feature_request.md) template for new ideas

## Code of Conduct

Please be respectful and constructive in all interactions. We are committed to providing a welcoming and inclusive experience for everyone.

## Questions?

Open a discussion on the [GitHub Discussions](https://github.com/zzj1965186613/agentforge/discussions) page.
