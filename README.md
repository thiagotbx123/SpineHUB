# TSA SpineHub Consolidation

Standard template structure for projects with Claude Code.

## What is it

**SpineHUB** is a set of routines and structures that ensure:
- Context persistence between sessions
- Automatic work documentation
- Git versioning
- Code quality (pre-commit hooks)
- Organized knowledge base
- Multi-user support

## How to Apply to a Project

### Method 1: Copy Structure
```bash
# Copy the entire structure to your project
cp -r SpineHUB/.claude YOUR_PROJECT/
cp -r SpineHUB/sessions YOUR_PROJECT/
cp -r SpineHUB/knowledge-base YOUR_PROJECT/
cp SpineHUB/CLAUDE.md YOUR_PROJECT/
cp SpineHUB/.gitignore YOUR_PROJECT/
cp SpineHUB/.pre-commit-config.yaml YOUR_PROJECT/
```

### Method 2: Use Claude command
Tell Claude:
> "Apply SpineHUB to the project [path]"

## Structure

```
SpineHUB/
├── .claude/
│   ├── commands/
│   │   ├── setup.md         # Initial setup for new users
│   │   ├── consolidar.md    # End of session routine
│   │   └── status.md        # Project overview
│   ├── memory.md            # Persistent state
│   ├── user-config.template.md  # User config template
│   └── settings.json        # Permissions
├── sessions/
│   ├── _template.md         # Session template
│   └── README.md            # Instructions
├── knowledge-base/
│   └── README.md            # Instructions
├── .env.template            # Credentials template
├── CLAUDE.md                # Mandatory instructions
├── .gitignore               # Git exclusions
├── .pre-commit-config.yaml  # Quality hooks
└── README.md                # This file
```

## Available Commands

| Command | When to Use |
|---------|-------------|
| `/setup` | First use or new user setup |
| `/status` | Start of session or when you need an overview |
| `/consolidar` | End of session to document work |

## Work Routine

```
1. Session Start
   └─> Claude reads memory.md automatically (via CLAUDE.md)
   └─> Checks if user is configured

2. During Work
   └─> Normal work, Claude maintains context

3. Session End
   └─> User runs /consolidar
       ├─> Documents session
       ├─> Updates memory.md
       ├─> Creates file in sessions/
       └─> Commit + Push to Git
```

## Projects Using SpineHUB

- `intuit-boom`
- `GEM-BOOM`
- `QBO WFS`
- `TSA_CORTEX`

---

**Created:** 2024-12-22
**Version:** 2.1 (renamed from ESPINHA_DORSAL, multi-user support)
