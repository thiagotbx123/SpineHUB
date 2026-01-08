# SpineHUB Credentials

This directory contains centralized credentials for all SpineHUB-managed projects.

## Setup

1. Copy `.env.template` to `.env.master`:
   ```bash
   cp .env.template .env.master
   ```

2. Fill in your tokens in `.env.master`

3. When you run `spinehub init` in a project, credentials will be linked automatically

## Security

- **NEVER commit `.env.master`** - it's in .gitignore
- Tokens should have minimal required permissions
- Rotate tokens regularly

## Token Creation Guides

### GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `workflow`
4. Copy token to `GITHUB_TOKEN`

### Slack Tokens
1. Go to https://api.slack.com/apps
2. Create or select your app
3. Go to OAuth & Permissions
4. Add scopes: `channels:history`, `channels:read`, `users:read`, `chat:write`
5. Install to workspace
6. Copy Bot Token to `SLACK_BOT_TOKEN`

### Linear API Key
1. Go to https://linear.app/settings/api
2. Create new API key
3. Copy to `LINEAR_API_KEY`

### Google Drive
1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 credentials
3. Download JSON
4. Set path in `GOOGLE_CREDENTIALS_PATH`

## Validation

Run to validate your credentials:
```bash
python -m spinehub validate credentials
```

## Per-Project Overrides

Projects can override master credentials by creating their own `.env` file.
The loading order is:
1. Project `.env` (highest priority)
2. SpineHUB `.env.master`
3. Environment variables
