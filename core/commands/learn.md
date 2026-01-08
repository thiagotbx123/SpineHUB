# /learn - Train Project Knowledge

Execute this routine to collect data from a project and feed it into the SpineHUB knowledge graph.

## PURPOSE

The `/learn` command:
1. Collects data from multiple sources (Claude history, Slack, local files)
2. Normalizes and deduplicates events
3. Extracts entities, relations, and patterns
4. Persists learning to the SpineHUB knowledge base

## USAGE

```bash
# Learn from current project (default: last 7 days)
/learn

# Learn from specific date range
/learn --days 30
/learn --start 2026-01-01 --end 2026-01-08

# Learn specific sources only
/learn --sources claude,local

# Dry run (show what would be collected)
/learn --dry-run
```

## MANDATORY STEPS

### STEP 1: Detect Context
```python
# Determine:
# - Current project path
# - Available collectors
# - Date range
# - SpineHUB data location
```

### STEP 2: Run Collectors
```python
from modules.collectors import run_all_collectors

# Collect from all configured sources
results = await run_all_collectors(config, date_range)

# Results contain:
# - events: Normalized ActivityEvent objects
# - errors: Any collection failures
# - warnings: Non-critical issues
```

### STEP 3: Normalize & Deduplicate
```python
# All events have deterministic IDs
# Duplicates are automatically filtered
# Events are sorted by timestamp
```

### STEP 4: Extract Knowledge
```python
from src.spinehub import SpineHub

hub = SpineHub("data/spinehub.json")

for event in events:
    # Extract entities (people, projects, channels)
    # Create relations (works_with, mentions, owns)
    # Track artifacts (files, documents)
    # Identify patterns (collaboration, workflow)
    hub.ingest_event(event)

hub.save()
```

### STEP 5: Report Results
```
============================================================
           LEARNING COMPLETE
============================================================

Project: [project_name]
Date Range: [start] to [end]

SOURCES COLLECTED:
  [OK] Claude: 142 events (92% noise filtered)
  [OK] Slack: 245 events
  [OK] Local: 38 files
  [--] Linear: Not configured
  [--] Drive: Not configured

KNOWLEDGE EXTRACTED:
  Entities: 47 new, 23 updated
  Relations: 89 new, 15 strengthened
  Artifacts: 38 tracked
  Patterns: 3 identified

STORAGE:
  [OK] Saved to data/spinehub.json
  [OK] Backup created

============================================================
```

## COLLECTORS AVAILABLE

| Collector | Source | Requires |
|-----------|--------|----------|
| Claude | ~/.claude/history.jsonl | Claude Code installed |
| Slack | Slack API | SLACK_USER_TOKEN, SLACK_USER_ID |
| Local | File system | Scan paths configured |
| Linear | Linear API | LINEAR_API_KEY (TODO) |
| Drive | Google Drive | OAuth credentials (TODO) |

## CONFIGURATION

Environment variables (in .env):
```
# Slack
SLACK_USER_TOKEN=xoxp-...
SLACK_BOT_TOKEN=xoxb-...
SLACK_USER_ID=U...

# Local scanning
LOCAL_SCAN_PATHS=~/Downloads,~/Documents,~/Projects

# Date range
LEARN_DEFAULT_DAYS=7
```

## NOTES

- Learning is additive - new events are merged with existing knowledge
- Deterministic IDs prevent duplicate entries on re-runs
- Backup is created before each save
- Use --dry-run to preview what would be collected
- SpineHUB data persists across sessions

---

## CLI USAGE

```bash
# Via SpineHUB CLI
python spinehub.py learn
python spinehub.py learn --days 14 --sources claude,slack

# Via Python module
python -c "from modules.collectors import run_all_collectors; ..."
```
