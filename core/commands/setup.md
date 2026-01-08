# /setup - SpineHUB Setup

Run this command to set up SpineHUB in a new project or configure a new user.

## MODES

### Mode 1: Project Setup (`spinehub init`)
Install SpineHUB structure in current directory.

### Mode 2: User Setup (`spinehub setup user`)
Configure user preferences and credentials.

### Mode 3: Credentials Setup (`spinehub setup credentials`)
Configure API tokens and secrets.

---

## PROJECT SETUP STEPS

### STEP 1: Detect Environment
```bash
# Check current directory
pwd

# Check if already initialized
test -d .claude && echo "SpineHUB already installed"

# Check git
git status 2>/dev/null || echo "Git not initialized"
```

### STEP 2: Create Structure
```
[project]/
├── .claude/
│   ├── commands/      # Symlink or copy from SpineHUB/core/commands
│   ├── memory.md      # From template
│   └── settings.json  # From template
├── sessions/
│   └── _template.md
├── knowledge-base/
│   └── README.md
├── CLAUDE.md          # From template, customized
└── .gitignore         # Append SpineHUB entries
```

### STEP 3: Configure Git (if needed)
```bash
# Initialize if needed
git init

# Configure user if not set
git config user.name || git config user.name "[name]"
git config user.email || git config user.email "[email]"
```

### STEP 4: Link Credentials
```bash
# Check if master credentials exist
test -f ~/SpineHUB/credentials/.env.master

# Create symlink or copy
ln -s ~/SpineHUB/credentials/.env.master .env
# OR
cp ~/SpineHUB/credentials/.env.template .env
```

### STEP 5: Register Project
```bash
# Add to SpineHUB registry
spinehub register [project-path]
```

### STEP 6: Initial Commit
```bash
git add .
git commit -m "spinehub: initial setup"
```

---

## USER SETUP STEPS

### STEP 1: Detect User
```bash
git config user.name
git config user.email
```

### STEP 2: Ask Preferences
- Preferred language (en/pt)
- Default services (Slack, Linear, Drive, GitHub)
- Notification preferences

### STEP 3: Create User Config
Save to `~/.spinehub/user.json`:
```json
{
  "name": "Thiago",
  "email": "thiago@example.com",
  "language": "en",
  "services": ["slack", "linear", "github", "drive"],
  "preferences": {
    "auto_commit": true,
    "auto_push": false,
    "session_reminders": true
  }
}
```

---

## CREDENTIALS SETUP STEPS

### STEP 1: List Required Credentials
Based on enabled services:
- GitHub: `GITHUB_TOKEN`
- Slack: `SLACK_BOT_TOKEN`, `SLACK_USER_TOKEN`
- Linear: `LINEAR_API_KEY`
- Drive: `GOOGLE_CREDENTIALS_PATH`

### STEP 2: Guide Token Creation
For each missing credential, provide:
- URL to create token
- Required scopes/permissions
- How to test the token

### STEP 3: Save to Master Credentials
```bash
# Save to ~/.spinehub/credentials/.env.master
echo "GITHUB_TOKEN=ghp_xxx" >> ~/.spinehub/credentials/.env.master
```

### STEP 4: Validate
```bash
spinehub validate credentials
```

---

## OUTPUT FORMAT

```
================================================================
  SpineHUB Setup Complete
================================================================

Project: [name]
Path: [path]
Version: SpineHUB 3.1

STRUCTURE CREATED:
  [OK] .claude/
  [OK] .claude/commands/ (3 commands)
  [OK] .claude/memory.md
  [OK] sessions/
  [OK] knowledge-base/
  [OK] CLAUDE.md

CONFIGURATION:
  [OK] Git initialized
  [OK] User: [name] <[email]>
  [OK] Credentials linked

NEXT STEPS:
  1. Review CLAUDE.md and customize for your project
  2. Run /status to verify setup
  3. Start working and use /consolidar at the end

================================================================
```
