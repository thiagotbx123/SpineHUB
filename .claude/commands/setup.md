# /setup - SpineHUB Initial Setup

Run this command when a new user is setting up SpineHUB for the first time.

## DETECTION LOGIC

### STEP 1: Check if user is already configured
Check if `.claude/user-config.md` exists:
- If exists and is filled: User already configured, show welcome message
- If doesn't exist or is empty: Start onboarding

### STEP 2: Automatic Onboarding
Try to detect automatically:

```bash
# Git name and email
git config user.name
git config user.email

# Operating system
uname -a  # Linux/Mac
ver       # Windows

# Home directory
echo $HOME  # Linux/Mac
echo %USERPROFILE%  # Windows
```

### STEP 3: Ask the User
If detection fails, ask:

1. **Full name**
2. **Primary email**
3. **Which services do you use?** (Slack, Linear, Drive, etc.)
4. **Preferred language for outputs**
5. **Main projects you'll work on**

### STEP 4: Create Configuration
1. Copy `.claude/user-config.template.md` to `.claude/user-config.md`
2. Fill in with collected information
3. Check if `.env` exists (if needed for APIs)
4. Test basic connections

### STEP 5: Configure Git (if needed)
If Git is not configured:
```bash
git config --global user.name "User Name"
git config --global user.email "email@example.com"
```

### STEP 6: Verify SpineHUB Structure
Confirm all directories exist:
- `.claude/` with commands and memory
- `sessions/`
- `knowledge-base/`
- `CLAUDE.md`

### STEP 7: Welcome Message
Present:
- Configuration summary
- Available commands (/status, /consolidar)
- Suggested next steps

---

## OUTPUT FORMAT

```
╔══════════════════════════════════════════════════════════════╗
║           SpineHUB - Initial Setup                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  User: [name]                                                ║
║  Email: [email]                                              ║
║  System: [OS]                                                ║
║                                                              ║
║  Detected Services:                                          ║
║  ✅ Git configured                                           ║
║  ⚠️  Slack (needs token setup)                               ║
║  ❌ Linear (not configured)                                  ║
║                                                              ║
║  Next Steps:                                                 ║
║  1. Configure your credentials in .env                       ║
║  2. Run /status to see current state                         ║
║  3. Use /consolidar at the end of each session               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Git not installed | Guide Git installation |
| Permission denied | Check directories and .gitignore |
| .env doesn't exist | Create .env template |
| Connection failed | Verify credentials and internet |
