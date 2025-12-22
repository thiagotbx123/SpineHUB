# SpineHUB Toolkit Installation Guide

> Complete guide to install all tools that enhance Claude Code productivity.
> This ensures any team member has the same powerful environment.

---

## Table of Contents

1. [Core CLI Tools](#1-core-cli-tools)
2. [Claude Code Setup](#2-claude-code-setup)
3. [Claude Desktop + MCP Servers](#3-claude-desktop--mcp-servers)
4. [Claude Plugins (Superpowers)](#4-claude-plugins-superpowers)
5. [Python Environment](#5-python-environment)
6. [Browser Automation (Playwright)](#6-browser-automation-playwright)
7. [Local AI (Ollama)](#7-local-ai-ollama)
8. [Desktop Applications](#8-desktop-applications)
9. [Network Tools (Tailscale)](#9-network-tools-tailscale)
10. [Recommended Claude Settings](#10-recommended-claude-settings)

---

## 1. Core CLI Tools

### Git
```bash
winget install Git.Git
```
**Version:** 2.52.0+
**Purpose:** Version control, required for SpineHUB

### GitHub CLI (gh)
```bash
winget install GitHub.cli
```
**Version:** 2.83.1+
**Purpose:** GitHub operations from terminal (PRs, issues, auth)

After install:
```bash
gh auth login --web --git-protocol https
```

### Node.js (LTS)
```bash
winget install OpenJS.NodeJS.LTS
```
**Version:** 24.11.1+
**Purpose:** Required for MCP servers and npm packages

### UV (Python package manager)
```bash
pip install uv
```
**Version:** 0.9.13+
**Purpose:** Fast Python package management (10-100x faster than pip)

---

## 2. Claude Code Setup

### Install Claude Code CLI
```bash
npm install -g @anthropic-ai/claude-code
```
**Version:** 2.0.75+

### First Run
```bash
claude
```
Follow the authentication flow.

### Enable Extended Thinking
Add to `~/.claude/settings.json`:
```json
{
  "alwaysThinkingEnabled": true
}
```

---

## 3. Claude Desktop + MCP Servers

### Install Claude Desktop
```bash
winget install Anthropic.Claude
```
**Purpose:** GUI version with MCP server support

### MCP Servers Available

| MCP Server | Purpose | Install |
|------------|---------|---------|
| **Desktop Commander** | File system, screenshot, clipboard | Via Claude Desktop marketplace |
| **Windows MCP** | Windows-specific operations | Via Claude Desktop marketplace |
| **Slack MCP** | Send/read Slack messages | `npx slack-mcp-server@latest` |
| **Linear MCP** | Issue tracking integration | Via marketplace |
| **GitHub MCP** | GitHub API operations | Via marketplace |
| **Playwright MCP** | Browser automation | Via marketplace |
| **Supabase MCP** | Database operations | Via marketplace |
| **Firebase MCP** | Firebase integration | Via marketplace |
| **Stripe MCP** | Payment processing | Via marketplace |

### Configuring MCP in Project

Create `.mcp.json` in project root:
```json
{
  "mcpServers": {
    "slack": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "slack-mcp-server@latest", "--transport", "stdio"],
      "env": {
        "SLACK_MCP_XOXC_TOKEN": "${SLACK_XOXC_TOKEN}",
        "SLACK_MCP_XOXD_TOKEN": "${SLACK_XOXD_TOKEN}"
      }
    }
  }
}
```

**IMPORTANT:** Never commit tokens! Use environment variables.

---

## 4. Claude Plugins (Superpowers)

### Install Superpowers Plugin
1. Open Claude Code CLI
2. Run: `/plugins`
3. Search for "superpowers"
4. Install "superpowers@superpowers-marketplace" v3.6.1+

### What Superpowers Adds
- Enhanced file operations
- Better code analysis
- Extended context management
- Additional slash commands

---

## 5. Python Environment

### Install Python
```bash
winget install Python.Python.3.13
# or for latest
winget install Python.Python.3.14
```

### Essential Packages

#### Core Development
```bash
pip install anthropic httpx fastapi uvicorn python-dotenv
```

#### Data Processing
```bash
pip install pandas numpy openpyxl xlrd xlsxwriter
```

#### Document Generation
```bash
pip install python-pptx python-docx pillow lxml
```

#### Browser Automation
```bash
pip install playwright pyautogui
playwright install
```

#### Google Integration
```bash
pip install google-api-python-client gspread google-auth-oauthlib
```

#### Slack Integration
```bash
pip install slack-bolt slack-sdk
```

#### Code Quality
```bash
pip install ruff pre-commit
```

#### Web Search (no API needed)
```bash
pip install duckduckgo_search
```

### Complete Install (One Command)
```bash
pip install anthropic httpx fastapi uvicorn python-dotenv pandas numpy openpyxl xlrd xlsxwriter python-pptx python-docx pillow lxml playwright pyautogui google-api-python-client gspread google-auth-oauthlib slack-bolt slack-sdk ruff pre-commit duckduckgo_search
```

---

## 6. Browser Automation (Playwright)

### Install Playwright
```bash
pip install playwright
playwright install
```

### Browsers Installed
- `chromium` - Main browser for automation
- `chromium_headless_shell` - Headless mode
- `ffmpeg` - Video/audio processing

### MCP Chrome Extension
Located at: `~\AppData\Local\ms-playwright\mcp-chrome`
Allows Claude to control Chrome via CDP (Chrome DevTools Protocol)

### Usage Example
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com")
    page.screenshot(path="screenshot.png")
    browser.close()
```

---

## 7. Local AI (Ollama)

### Install Ollama
```bash
winget install Ollama.Ollama
```

### Download Models
```bash
ollama pull gemma3:4b      # 3.3GB - Fast, good quality
ollama pull llama3.2       # 2.0GB - Balanced
```

### Use Cases
- Offline AI processing
- Local embeddings
- Privacy-sensitive tasks
- Cost reduction for simple queries

### Run Model
```bash
ollama run gemma3:4b
```

---

## 8. Desktop Applications

### Productivity Apps

| App | Install Command | Purpose |
|-----|-----------------|---------|
| **Google Chrome** | `winget install Google.Chrome` | Web automation, DevTools |
| **Chrome Remote Desktop** | `winget install Google.ChromeRemoteDesktopHost` | Remote access |
| **Linear** | `winget install LinearOrbit.Linear` | Issue tracking |
| **Slack** | `winget install SlackTechnologies.Slack` | Team communication |

### All-in-One Install
```bash
winget install Google.Chrome
winget install Google.ChromeRemoteDesktopHost
winget install LinearOrbit.Linear
winget install SlackTechnologies.Slack
winget install Ollama.Ollama
winget install Anthropic.Claude
winget install GitHub.cli
winget install Git.Git
winget install OpenJS.NodeJS.LTS
winget install Python.Python.3.14
```

---

## 9. Network Tools (Tailscale)

### Install Tailscale
```bash
winget install Tailscale.Tailscale
```

### Purpose
- Secure VPN mesh network
- Access team machines
- No port forwarding needed
- Works through firewalls

### Setup
1. Install Tailscale
2. Run `tailscale up`
3. Authenticate with team account
4. Access machines by hostname

### Check Status
```bash
tailscale status
```

---

## 10. Recommended Claude Settings

### Global Settings (`~/.claude/settings.json`)
```json
{
  "permissions": {
    "allow": [
      "Bash",
      "Read",
      "Write",
      "Edit",
      "Glob",
      "Grep",
      "WebFetch",
      "WebSearch",
      "Task",
      "NotebookEdit"
    ]
  },
  "alwaysThinkingEnabled": true
}
```

### Local Project Settings (`.claude/settings.local.json`)

For commonly used commands, add auto-permissions:
```json
{
  "permissions": {
    "allow": [
      "Bash(pip install:*)",
      "Bash(python:*)",
      "Bash(git:*)",
      "Bash(npm:*)",
      "Bash(ruff:*)",
      "Bash(pre-commit:*)"
    ]
  }
}
```

---

## Quick Start Checklist

### Minimum Setup (10 minutes)
- [ ] Install Git
- [ ] Install GitHub CLI + authenticate
- [ ] Install Node.js
- [ ] Install Claude Code CLI
- [ ] Enable extended thinking

### Full Setup (30 minutes)
- [ ] All minimum setup
- [ ] Install Python 3.13+
- [ ] Install Python packages
- [ ] Install Playwright + browsers
- [ ] Install Claude Desktop
- [ ] Install Superpowers plugin
- [ ] Configure MCP servers needed

### Team Setup (Optional)
- [ ] Install Tailscale
- [ ] Install Slack
- [ ] Install Linear
- [ ] Configure team MCP tokens

---

## Version Reference

| Tool | Version | Check Command |
|------|---------|---------------|
| Git | 2.52.0+ | `git --version` |
| GitHub CLI | 2.83.1+ | `gh --version` |
| Node.js | 24.11.1+ | `node --version` |
| npm | 11.6.2+ | `npm --version` |
| Python | 3.13+ | `python --version` |
| UV | 0.9.13+ | `uv --version` |
| Claude Code | 2.0.75+ | `claude --version` |
| Playwright | 1.56.0+ | `playwright --version` |
| Ollama | 0.13.5+ | `ollama --version` |
| Ruff | 0.14.8+ | `ruff --version` |

---

## Troubleshooting

### Claude Code not found
```bash
npm install -g @anthropic-ai/claude-code
```

### Playwright browsers not working
```bash
playwright install --force
```

### Git authentication issues
```bash
gh auth login --web
git config --global credential.helper manager
```

### Python packages conflict
```bash
uv pip install --upgrade <package>
```

---

*Last updated: 2025-12-22*
*SpineHUB v2.1*
