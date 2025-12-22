# TSA SpineHub Consolidation - Instructions for Claude

> **MANDATORY READING** - This file contains instructions that Claude MUST follow in EVERY session.

---

## Session Start Protocol

**BEFORE responding to anything, ALWAYS execute these steps IN ORDER:**

### 1. Detect User
Check if `.claude/user-config.md` exists:
- **If NOT exists:** Run `/setup` to configure the new user
- **If exists:** Read it to know the user and their preferences

### 2. Recover Context
Read `.claude/memory.md` to understand:
- Current project phase
- Last actions performed
- Known blockers
- Pending next steps

### 3. Check Previous Sessions
Check `sessions/` for:
- Last registered session
- Recent unconsolidated work
- Additional context

### 4. Consult Knowledge Base (if needed)
Check `knowledge-base/` for:
- API documentation
- Architectural decisions
- Known troubleshooting

---

## New User Protocol

If the user is NOT configured (`.claude/user-config.md` doesn't exist):

1. **Try to detect automatically:**
   ```bash
   git config user.name
   git config user.email
   ```

2. **If successful:** Create the configuration with detected data

3. **If NOT successful:** Ask the user:
   - Full name
   - Email
   - Which services they use (Slack, Linear, Drive, etc.)
   - Preferred language

4. **Create necessary files** and guide them on next steps

---

## Session End Protocol

**When finishing work, ALWAYS run `/consolidar`:**

1. Document what was done
2. Update memory.md
3. Create session file in `sessions/YYYY-MM-DD_HH-MM.md`
4. Commit and push to Git (if configured)

---

## Available Commands

| Command | Function | When to Use |
|---------|----------|-------------|
| `/setup` | Initial setup | First use or new user |
| `/status` | Project overview | Start of session |
| `/consolidar` | Save session | End of each work session |

---

## Golden Rules

1. **Detect the user** - Always check user-config.md first
2. **Never lose context** - Always read memory.md
3. **Always document** - Use /consolidar at the end
4. **Maintain history** - Never delete sessions or knowledge
5. **Git is mandatory** - All work must be versioned
6. **Guide the user** - If something isn't configured, teach how to do it

---

## Project Structure

```
SpineHUB/
├── .claude/
│   ├── commands/
│   │   ├── setup.md        # Initial setup
│   │   ├── status.md       # Overview
│   │   └── consolidar.md   # End of session
│   ├── memory.md           # Persistent state
│   ├── user-config.md      # User config (DO NOT COMMIT)
│   ├── user-config.template.md  # Template for new users
│   └── settings.json       # Claude permissions
├── sessions/               # Session history
├── knowledge-base/         # Knowledge base
├── .env                    # Credentials (DO NOT COMMIT)
├── .env.template           # Credentials template
├── CLAUDE.md               # This file
├── .gitignore              # Git exclusions
└── .pre-commit-config.yaml # Quality hooks
```

---

## Sensitive Files (DO NOT COMMIT)

These files contain user-specific data and should NOT be versioned:

| File | Content |
|------|---------|
| `.claude/user-config.md` | User's personal data |
| `.env` | Credentials and tokens |
| `*_secret*` | Any file with "secret" in the name |
| `*_token*` | Any file with "token" in the name |

---

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                      SESSION START                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ user-config.md  │
                    │    exists?      │
                    └─────────────────┘
                         │      │
                     NO  │      │  YES
                         ▼      ▼
              ┌──────────────┐  ┌──────────────┐
              │   /setup     │  │ Read user    │
              │  (onboard)   │  │ config       │
              └──────────────┘  └──────────────┘
                         │      │
                         └──────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Read memory.md  │
                    │ and sessions/   │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │      WORK       │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  /consolidar    │
                    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       SESSION END                           │
└─────────────────────────────────────────────────────────────┘
```

---

**IMPORTANT:** These instructions ensure continuity, quality, and portability across users and sessions.
