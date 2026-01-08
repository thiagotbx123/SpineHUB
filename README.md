# SpineHUB

**Knowledge Graph System with Code Analysis**

SpineHUB is a comprehensive system for maintaining persistent memory across Claude Code sessions, building knowledge graphs from multiple sources, and analyzing code quality with integrated tools.

## Features

### 1. Knowledge Graph (SpineHUB Core)
- **Entity Management**: Track people, projects, channels, topics, teams
- **Relations**: Model connections between entities (works_with, mentions, owns)
- **Artifacts**: Track files and documents with URLs
- **Patterns**: Identify recurring patterns across sessions

### 2. Code Analysis (Integrated Tools)
- **Ruff**: Fast Python linter (10-100x faster than flake8)
- **Bandit**: Security scanner (SQL injection, command injection, etc.)
- **Vulture**: Dead code detector
- **Radon**: Cyclomatic complexity analyzer (A-F scale)

### 3. Quality Validation
- **Worklog Validator**: Ensures worklogs follow RAC-14 standard
  - English-only content
  - Third person narrative
  - No Slack quotes
  - Required sections (Summary, Artifacts, Outcome)

### 4. Session Management
- Context persistence between sessions
- Automatic work documentation
- Git versioning
- Multi-user support

## Installation

```bash
# Clone or copy to your project
git clone https://github.com/thiagotbx123/SpineHUB.git

# Install dependencies
pip install -r requirements.txt
```

## Usage

### CLI Commands

```bash
# Run code analysis on a project
python -m src.cli analyze --path /path/to/project

# Run specific tool
python -m src.cli analyze --tool ruff

# Show SpineHUB statistics
python -m src.cli stats

# Validate a worklog file
python -m src.cli validate worklog.md
```

### Python API

```python
from src.spinehub import SpineHub, Entity, EntityType

# Create SpineHUB instance
hub = SpineHub("data/spinehub.json")

# Ingest data from Slack
hub.ingest_slack_message(
    text="Hey @Katherine, can we discuss WFS?",
    channel="project-wfs",
    sender="Thiago",
    timestamp=datetime.now(),
    is_my_work=True,
)

# Get narrative context
context = hub.get_narrative_context(topic="wfs")

# Save data
hub.save()
```

### Code Analysis

```python
from src.analyzers import CodeAnalyzer

analyzer = CodeAnalyzer("/path/to/project")

# Check available tools
tools = analyzer.check_tools()
print(tools)  # {'ruff': True, 'bandit': True, ...}

# Run all analyzers
result = analyzer.run_all()
print(result.format_report())

# Run single tool
ruff_result = analyzer.run_single("ruff")
```

### Quality Validation

```python
from src.spinehub import validate_worklog

content = open("worklog.md").read()
passed, report = validate_worklog(content)
print(report)
```

## Project Structure

```
SpineHUB/
├── src/
│   ├── spinehub/           # Knowledge graph core
│   │   ├── __init__.py
│   │   ├── entities.py     # Entity, Relation, Artifact, Pattern
│   │   ├── storage.py      # JSON persistence layer
│   │   ├── core.py         # SpineHub engine
│   │   └── benchmark.py    # Quality validator
│   ├── analyzers/          # Code analysis tools
│   │   ├── __init__.py
│   │   ├── analyzer_base.py
│   │   └── code_analyzer.py
│   └── cli.py              # Command-line interface
├── tests/                  # Test suite
├── .claude/                # Claude Code config
│   ├── commands/           # Slash commands
│   ├── memory.md           # Persistent state
│   └── settings.json       # Permissions
├── sessions/               # Session history
├── knowledge-base/         # Documentation
├── data/                   # SpineHUB data storage
├── requirements.txt        # Dependencies
├── CLAUDE.md               # Instructions for Claude
└── README.md               # This file
```

## Slash Commands

| Command | Description |
|---------|-------------|
| `/setup` | Configure new user |
| `/status` | Show project status |
| `/consolidar` | Save session and commit |

## Projects Using SpineHUB

| Project | Type | SpineHUB Features Used |
|---------|------|------------------------|
| TSA_CORTEX | TypeScript | Full knowledge graph + collectors |
| intuit-boom | Python | Structure + Strategic Cortex |
| GEM-BOOM | Python | Structure + API docs |
| QBO WFS | Python | Structure + .context/ |

## Analysis Tool Details

### Ruff
- Checks style (E), warnings (W), imports (I), pyflakes (F)
- Fix available for most issues
- 10-100x faster than traditional linters

### Bandit
- Security-focused analysis
- Detects: SQL injection (B608), command injection (B602)
- Finds hardcoded passwords and unsafe deserialization

### Vulture
- Finds unused code (functions, classes, variables, imports)
- Configurable confidence threshold
- Helps reduce code bloat

### Radon
- Calculates cyclomatic complexity
- Grades: A (simple) to F (complex)
- Helps identify refactoring opportunities

## Development

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-22 | Initial (ESPINHA_DORSAL) |
| 2.0 | 2024-12-22 | Renamed to SpineHUB |
| 2.1 | 2025-12-22 | Multi-user + English |
| 3.0 | 2026-01-08 | Python implementation + Code analyzers |

---

**Maintained by:** Thiago Rodrigues (TSA)
**Repository:** https://github.com/thiagotbx123/SpineHUB
