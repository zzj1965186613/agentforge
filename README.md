# AgentForge

**The definitive skill manager for AI agents — discover, install, and manage agent skills from the command line.**

[![CI](https://github.com/zzj1965186613/agentforge/actions/workflows/ci.yml/badge.svg)](https://github.com/zzj1965186613/agentforge/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/agentforge)](https://pypi.org/project/agentforge/)
[![Python](https://img.shields.io/pypi/pyversions/agentforge)](https://pypi.org/project/agentforge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Quick Start

### Install

```bash
pip install agentforge
```

### 3-Command Quickstart

```bash
# 1. Search for a skill
agentforge search code review

# 2. Get details about a skill
agentforge info code-review

# 3. Install it
agentforge install code-review
```

That's it — you're up and running!

---

## 📦 Available Skills

<!-- SKILL_TABLE_START -->
| Skill | Category | Description |
|-------|----------|-------------|
| [prompt-engineering](skills/ai-ml/prompt-engineering.md) | ai-ml | Prompt engineering patterns and techniques for effective LLM interactions |
| [microservices](skills/architecture/microservices.md) | architecture | Microservices architecture patterns, decomposition strategies, and operational best practices |
| [system-design](skills/architecture/system-design.md) | architecture | System design methodology for building scalable, reliable, and maintainable distributed systems |
| [api-design](skills/coding/api-design.md) | coding | RESTful API design patterns, conventions, and best practices |
| [clean-code](skills/coding/clean-code.md) | coding | Clean code principles, patterns, and practical guidelines for maintainable software |
| [code-review](skills/coding/code-review.md) | coding | Perform thorough code reviews covering correctness, security, performance, and style |
| [debugging](skills/coding/debugging.md) | coding | Structured debugging methodology: reproduce, isolate, fix, and verify |
| [performance-optimization](skills/coding/performance-optimization.md) | coding | Profiling, bottleneck identification, and systematic performance optimization |
| [refactoring](skills/coding/refactoring.md) | coding | Systematic refactoring with safety checks, preserving behaviour while improving structure |
| [security-audit](skills/coding/security-audit.md) | coding | OWASP-based security audit checklist for application code and infrastructure |
| [test-writing](skills/coding/test-writing.md) | coding | TDD-style test writing with coverage goals and best practices |
| [ci-cd-pipeline](skills/devops/ci-cd-pipeline.md) | devops | GitHub Actions CI/CD pipeline design with best practices for testing, building, and deploying |
| [docker-optimization](skills/devops/docker-optimization.md) | devops | Docker best practices for efficient, secure, and production-ready container images |
| [documentation](skills/workflows/documentation.md) | workflows | Technical documentation writing guide for READMEs, API docs, architecture docs, and user guides |
| [git-workflow](skills/workflows/git-workflow.md) | workflows | Git branching strategies, commit conventions, and collaboration best practices |
<!-- SKILL_TABLE_END -->

---

## ✨ Features

- **🔍 Discover** — Search and browse a curated registry of AI agent skills
- **📥 Install** — One-command skill installation with dependency resolution
- **🔄 Update** — Keep your skills up to date with a single command
- **📤 Share** — Export and share skills via JSON or GitHub Gists
- **⚙️ Configure** — Flexible configuration per-agent or globally
- **🎯 Multi-Agent** — Manage skills across multiple agents independently

---

## 📖 Usage

```bash
# List all available skills
agentforge list

# List only installed skills
agentforge list --installed

# Search for skills
agentforge search <query>

# Get detailed info about a skill
agentforge info <skill-name>

# Install one or more skills
agentforge install <skill-name> [<skill-name> ...]

# Uninstall a skill
agentforge uninstall <skill-name>

# Update skills
agentforge update --all

# Share a skill
agentforge share <skill-name> --output ./skill.json

# Manage configuration
agentforge config show
agentforge config set <key> <value>
```

### Global Options

```
--version       Show version and exit
-v, --verbose   Enable verbose output
-c, --config    Path to a custom config file
```

---

## 🛠 Development

```bash
# Clone the repository
git clone https://github.com/zzj1965186613/agentforge.git
cd agentforge

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](.github/CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-skill`)
3. Commit your changes (`git commit -m 'Add amazing skill'`)
4. Push to the branch (`git push origin feature/amazing-skill`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built for the [Hermes Agent](https://github.com/nousresearch/hermes-agent) ecosystem by Nous Research.
