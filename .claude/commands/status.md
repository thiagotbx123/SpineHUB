# /status - Project Status

Run to get an overview of the current project state.

## WHAT TO CHECK

### 1. Project State
Read `.claude/memory.md` and present:
- Current phase
- Recent actions performed
- Known blockers

### 2. Knowledge Base
List files in `knowledge-base/`:
- Number of documents
- Last update

### 3. Sessions
Check `sessions/`:
- Total registered sessions
- Last session (date and summary)

### 4. Git Status
Run and present:
```bash
git status
git log --oneline -5
```

### 5. Next Actions
Based on context, suggest 3 priority next actions.

---

## OUTPUT FORMAT

```
📊 PROJECT STATUS: [name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Current Phase: [phase]
📅 Last Session: [date]
📚 Knowledge Base: [X] documents
🔄 Git: [X] commits, branch [name]

⚠️ Blockers:
- [blocker 1]
- [blocker 2]

✅ Recent Actions:
- [action 1]
- [action 2]

🎯 Next Steps:
1. [priority action 1]
2. [priority action 2]
3. [priority action 3]
```
