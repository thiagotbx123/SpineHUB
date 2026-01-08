# /consolidar - Session Consolidation

Execute this routine at the END of each work session to preserve knowledge.

## MANDATORY STEPS

### STEP 1: Detect Context
```python
# This is handled by SpineHUB CLI
# Detects: HOME vs PROJECT, git status, pending changes
```

### STEP 2: Session Analysis
Analyze what was done in this session:
- Decisions made
- New knowledge acquired
- Files created/modified
- Problems solved
- Tasks completed
- New tasks identified

### STEP 3: Create Session File
Create file in `sessions/YYYY-MM-DD_description.md`:

```markdown
# Session: YYYY-MM-DD - [Brief Description]

## Summary
[2-3 sentences describing what was accomplished]

## Changes Made
- [file1]: [what changed]
- [file2]: [what changed]

## Decisions
- [decision 1]: [rationale]

## Learnings
- [learning 1]

## Next Steps
- [ ] [task 1]
- [ ] [task 2]

## Git
- Commit: [hash]
- Branch: [branch name]
```

### STEP 4: Update Memory
Update `.claude/memory.md` with:
- Current project state
- Recent actions performed
- Known blockers
- Suggested next steps

### STEP 5: Git Versioning
```bash
# SpineHUB handles this via git_manager module
spinehub git commit --auto-message
spinehub git push
```

Or manually:
```bash
git add .
git commit -m "consolidar: [brief session summary]"
git push
```

### STEP 6: Final Report
Present to user:
```
==============================================================
           CONSOLIDATION COMPLETE
==============================================================

Project: [name]
Date: [current date]
Session: [duration]

FILES UPDATED:
  [OK] .claude/memory.md
  [OK] sessions/YYYY-MM-DD_description.md
  [OK] [other files]

GIT:
  [OK] Commit: [hash] - [message]
  [OK] Push: origin/[branch]

NEXT STEPS:
  1. [action 1]
  2. [action 2]

==============================================================
```

---

## NOTES

- If in HOME, update only global memory.md
- If in project, update project memory.md + create session file
- ALWAYS git commit if repository available
- NEVER lose knowledge - document everything
