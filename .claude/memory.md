# Memory - Project Persistent State

> This file maintains context between sessions. Update at the end of each session via `/consolidar`.

## Current State

**Phase:** Production (v3.0 - Complete Rewrite with Collectors)
**Last Update:** 2026-01-08
**Current User:** See .claude/user-config.md

## Recent Actions

| Date | Action | Result | User |
|------|--------|--------|------|
| 2026-01-08 | SpineHUB v3.0 complete rewrite | Collectors, knowledge graph, learn command | Thiago |
| 2026-01-08 | Port collectors from TSA_CORTEX | ClaudeCollector, SlackCollector, LocalCollector | Thiago |
| 2026-01-08 | Implement learn command | `spinehub learn --days 7 --sources claude,slack,local` | Thiago |
| 2026-01-08 | Implement activate command | `spinehub activate install` for global support | Thiago |
| 2025-12-22 | Toolkit inventory scan | 189+ components documented in Excel | Thiago |
| 2025-12-22 | Full English translation | 14 files translated, pushed to GitHub | Thiago |

## Known Blockers

- [ ] None currently - project is fully functional

## Important Decisions

| Date | Decision | Context | Decided by |
|------|----------|---------|------------|
| 2025-12-22 | Create Excel inventory | User wanted complete list, not install guide | Thiago |
| 2025-12-22 | English as primary language | GitHub international audience | Thiago |
| 2025-12-22 | Auto-detect user via git config | Frictionless onboarding | Thiago |
| 2025-12-22 | user-config.md gitignored | Privacy - personal data not shared | Thiago |

## Key Learnings (Permanent)

### Toolkit Inventory (189+ components)
```
Python Packages:    84  (anthropic, pandas, playwright, slack, etc)
CLI Tools:          12  (git, gh, node, python, ruff, etc)
Desktop Apps:        8  (Chrome, Slack, Linear, Tailscale, etc)
MCP Servers:        15  (Desktop Commander, Slack, GitHub, etc)
Claude Plugins:     12  (Superpowers 3.6.1, Code Review, etc)
Ollama Models:       2  (gemma3:4b, llama3.2)
Playwright:          5  (chromium, mcp-chrome, ffmpeg)
Tailscale:         40+ machines in team network
```

### Key Tools Discovered
| Tool | Version | Purpose |
|------|---------|---------|
| Claude Code CLI | 2.0.75 | Main AI assistant |
| Superpowers Plugin | 3.6.1 | Enhanced capabilities |
| Desktop Commander MCP | Enabled | File system, screenshots |
| Playwright | 1.56.0 | Browser automation |
| Tailscale | 1.88.1 | Team VPN network |

### Multi-User Architecture
```
Flow: user-config.md exists?
  ├─ NO → Run /setup → Auto-detect git config → Create user-config.md
  └─ YES → Read user preferences → Continue session
```

### Template Pattern
- Files ending in `.template` are meant to be copied and customized
- Original templates stay in repo, customized versions are gitignored
- Examples: `.env.template` → `.env`, `user-config.template.md` → `user-config.md`

### Session Persistence Strategy
1. **memory.md** - Current state, recent actions, blockers
2. **sessions/** - Historical record of each session
3. **knowledge-base/** - Permanent reference documentation

## Session Notes

### 2025-12-22 (Session 2) - Thiago
- **Achievements:** Complete toolkit scan, Excel inventory created
- **Learnings:** 189+ tools/packages installed, Tailscale has 40+ team machines
- **Files Created:** TOOLKIT_INVENTORY.xlsx, TOOLKIT_INSTALLATION_GUIDE.md
- **Next:** Share toolkit with team for standardization

### 2025-12-22 (Session 1) - Thiago
- **Achievements:** v2.1 release with multi-user + English
- **Learnings:** Auto-detection via git config works great
- **Next:** Test with other team members

---

## Project History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2024-12-22 | Created as ESPINHA_DORSAL |
| 2.0 | 2024-12-22 | Renamed to SpineHUB |
| 2.1 | 2025-12-22 | Multi-user support + English translation |
| 2.2 | 2025-12-22 | Toolkit documentation + Excel inventory |
| 3.0 | 2026-01-08 | Complete rewrite: collectors, knowledge graph, learn command |

## Available Commands

### Slash Commands (Claude)
| Command | Purpose |
|---------|---------|
| /setup | Configure new user (auto-detection + guided) |
| /status | Show project overview and current state |
| /consolidar | Save session, update memory, commit |

### CLI Commands (spinehub.py)
| Command | Purpose |
|---------|---------|
| `spinehub learn` | Collect activity from sources (claude, slack, local) |
| `spinehub activate` | Install SpineHUB globally for cross-project support |
| `spinehub init` | Install SpineHUB in any project |
| `spinehub sync` | Sync commands across registered projects |
| `spinehub git` | Git operations (status, commit, consolidar, push, pull) |
| `spinehub status` | Show current project status |
| `spinehub list` | List registered projects |

### Collectors Available
| Collector | Source | Status |
|-----------|--------|--------|
| ClaudeCollector | ~/.claude/history.jsonl, sessions | Implemented |
| SlackCollector | Slack API (search) | Implemented (requires tokens) |
| LocalCollector | File system scanning | Implemented |
| LinearCollector | Linear API | TODO |
| DriveCollector | Google Drive | TODO |

## Key Files Reference

| File | Purpose |
|------|---------|
| `TOOLKIT_INVENTORY.xlsx` | Complete Excel with all 189+ tools |
| `knowledge-base/TOOLKIT_INSTALLATION_GUIDE.md` | Installation guide for new users |
| `sessions/2025-12-22_toolkit-scan.md` | Session record |

## Repository

- **GitHub:** https://github.com/thiagotbx123/SpineHUB
- **Branch:** master
- **Latest commit:** docs: Complete toolkit installation guide

---

**Instructions:** Always read this file at the start of each session to recover context.
