# /consolidar - Session Consolidation

Run this routine at the END of each work session to preserve knowledge.

## MANDATORY STEPS

### STEP 1: Session Analysis
Analyze what was done in this session:
- Decisions made
- New knowledge acquired
- Files created/modified
- Problems solved
- Tasks completed
- New tasks identified

### STEP 2: Create Session File
Create file in `sessions/YYYY-MM-DD_HH-MM.md` using the template `sessions/_template.md`

### STEP 3: Update Knowledge Base
Update relevant files in `knowledge-base/`:
- New learnings
- API/integration documentation
- Discovered troubleshooting

### STEP 4: Update Memory
Update `.claude/memory.md` with:
- Current project state
- Recent actions performed
- Known blockers
- Suggested next steps

### STEP 5: Commit and Push
Run:
```bash
git add .
git commit -m "consolidar: [brief session summary]"
git push
```

### STEP 6: Final Report
Present to user:
- Summary of what was consolidated
- Updated files
- Commit made
- Suggested next steps

---

**IMPORTANT:** This routine ensures no knowledge is lost between sessions.
