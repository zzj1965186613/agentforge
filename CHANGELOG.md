# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-19

### Added

- Initial release of AgentForge.
- CLI tool with Click framework and Rich output formatting.
- `agentforge list` — List available and installed skills with table/JSON/names output.
- `agentforge search` — Fuzzy search across skill names, descriptions, and tags.
- `agentforge info` — Detailed skill information panel.
- `agentforge install` — Install skills with agent, global, force, and dry-run options.
- `agentforge uninstall` — Remove installed skills.
- `agentforge init` — Interactive agent configuration setup.
- `agentforge update` — Update individual or all installed skills.
- `agentforge share` — Export skills to JSON or create GitHub Gists.
- `agentforge config` — Show, set, and reset configuration.
- Python package with hatchling build backend.
- GitHub Actions CI/CD pipeline for testing and PyPI publishing.
- MIT License.
