# /status - Project Status

Run to get an overview of the current project state.

## WHAT TO CHECK

### 1. Project Detection
```python
# SpineHUB CLI handles this
# Detects: project name, SpineHUB version, completeness
```

### 2. Memory State
Read `.claude/memory.md` and present:
- Current phase
- Recent actions performed
- Known blockers

### 3. Knowledge Base
List files in `knowledge-base/`:
- Number of documents
- Last update
- Key topics covered

### 4. Sessions
Check `sessions/`:
- Total registered sessions
- Last session (date and summary)
- Session frequency

### 5. Git Status
```bash
git status --short
git log --oneline -5
git remote -v
```

### 6. SpineHUB Health
Check:
- [ ] .claude/memory.md exists and is recent
- [ ] CLAUDE.md exists
- [ ] sessions/ directory exists
- [ ] knowledge-base/ directory exists
- [ ] Git is configured
- [ ] Credentials are set (if needed)

### 7. Next Actions
Based on context, suggest 3 priority next actions.

---

## OUTPUT FORMAT

```
================================================================
  PROJECT STATUS: [name]
================================================================

Phase: [phase]
Last Session: [date] ([X] days ago)
SpineHUB: [version] - [health status]

STRUCTURE:
  [OK] .claude/memory.md (updated [date])
  [OK] CLAUDE.md
  [OK] sessions/ ([X] files)
  [OK] knowledge-base/ ([X] files)
  [OK] Git configured (branch: [name])

BLOCKERS:
  - [blocker 1]
  - [blocker 2]

RECENT ACTIONS:
  - [date]: [action 1]
  - [date]: [action 2]

NEXT STEPS:
  1. [priority action 1]
  2. [priority action 2]
  3. [priority action 3]

================================================================
```

---

## QUICK STATUS (--short flag)

```
[project] | Phase: [phase] | Last: [date] | Git: [branch] [clean/dirty]
```
