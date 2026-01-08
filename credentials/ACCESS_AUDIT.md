# SpineHUB Access Audit - Analise Completa

> Gerado em: 2026-01-08
> Objetivo: Identificar gaps de acesso entre SpineHUB e outros projetos

## Resumo Executivo

| Status | Quantidade |
|--------|------------|
| SpineHUB TEM | 6 tipos |
| SpineHUB NAO TEM | 5 tipos |
| MCPs Globais | 10 servidores |

---

## 1. MCPs Configurados (Claude Desktop)

### Ativos no Sistema
| MCP Server | Status | Funcao |
|------------|--------|--------|
| playwright | OK | Automacao Chrome/browser |
| slack | OK | Acesso direto Slack (xoxc/xoxd) |
| qb-construction | OK | QuickBooks Sandbox |
| qb-terra | OK | QuickBooks Production |
| qb-bluecraft | OK | QuickBooks Production |
| qb-ironcraft | OK | QuickBooks Production |
| qb-stonecraft | OK | QuickBooks Production |
| qb-canopy | OK | QuickBooks Production |
| qb-ecocraft | OK | QuickBooks Production |
| qb-volt | OK | QuickBooks Production |

### FALTANDO (mencionados mas nao configurados)
| MCP Server | Status | Onde Deveria Estar |
|------------|--------|-------------------|
| desktop-commander | FALTANDO | File system, screenshots, clipboard |
| github | FALTANDO | GitHub API nativo |
| linear | FALTANDO | Linear API nativo |
| google-drive | FALTANDO | Google Drive API |

---

## 2. Credenciais por Projeto

### Matriz de Credenciais

| Servico | SpineHUB | TSA_CORTEX | SLACK_MONITOR | GEM-BOOM | LINEAR_AUTO | QBO WFS |
|---------|----------|------------|---------------|----------|-------------|---------|
| Slack Bot (xoxb) | template | REAL | REAL | - | - | - |
| Slack User (xoxp) | template | REAL | REAL | - | - | REAL |
| Slack MCP (xoxc) | - | - | - | - | - | - |
| Slack MCP (xoxd) | - | - | - | - | - | - |
| Slack User ID | - | REAL | - | - | - | REAL |
| Linear API | template | REAL | - | - | REAL | - |
| Google Client ID | template | REAL | - | - | - | - |
| Google Secret | template | REAL | - | - | - | - |
| Google Refresh | template | REAL | - | - | - | - |
| Gem API | - | - | - | REAL | - | - |
| QuickBooks | - | Via MCP | - | - | - | Via MCP |
| Anthropic | template | - | - | template | - | - |
| GitHub | template | - | - | - | - | - |

### Legenda
- **REAL** = Credencial real preenchida
- **template** = Apenas template, nao preenchido
- **Via MCP** = Acesso via MCP server global
- **-** = Nao tem

---

## 3. Gaps Criticos do SpineHUB

### Categoria 1: NAO TEM e PRECISA
| Item | Fonte | Acao |
|------|-------|------|
| Slack MCP tokens (xoxc/xoxd) | claude_desktop_config.json | Copiar para .env |
| Slack User ID | TSA_CORTEX | Copiar para .env |
| Gem API Key | GEM-BOOM | Copiar para .env |
| Desktop Commander MCP | Nao configurado | Adicionar ao sistema |

### Categoria 2: TEM TEMPLATE mas NAO PREENCHIDO
| Item | Fonte para Copiar |
|------|-------------------|
| Slack Bot Token | TSA_CORTEX ou SLACK_MONITOR |
| Slack User Token | TSA_CORTEX ou SLACK_MONITOR |
| Linear API Key | TSA_CORTEX ou LINEAR_AUTO |
| Google OAuth | TSA_CORTEX |
| Anthropic API | Console Anthropic |
| GitHub Token | GitHub Settings |

### Categoria 3: MCP NAO CENTRALIZADO
O SpineHUB deveria ter referencia para MCPs mas nao controla eles diretamente.
MCPs sao configurados em: `%APPDATA%/Claude/claude_desktop_config.json`

---

## 4. Valores Encontrados (Referencias)

> **NOTA**: Valores reais estao em `.env.master` (gitignored). Este arquivo mostra apenas o formato.

### Slack (de TSA_CORTEX)
```
SLACK_BOT_TOKEN=xoxb-***-***-*** (ver .env.master)
SLACK_USER_TOKEN=xoxp-***-***-***-*** (ver .env.master)
SLACK_USER_ID=U********* (ver .env.master)
```

### Slack MCP (de claude_desktop_config.json)
```
SLACK_MCP_XOXC_TOKEN=xoxc-***-***-***-*** (ver claude_desktop_config.json)
SLACK_MCP_XOXD_TOKEN=xoxd-*** (ver claude_desktop_config.json)
```

### Linear (de TSA_CORTEX)
```
LINEAR_API_KEY=lin_api_*** (ver .env.master)
```

### Google Drive (de TSA_CORTEX)
```
GOOGLE_CLIENT_ID=***.apps.googleusercontent.com (ver .env.master)
GOOGLE_CLIENT_SECRET=GOCSPX-*** (ver .env.master)
GOOGLE_REFRESH_TOKEN=1//*** (ver .env.master)
```

### Gem (de GEM-BOOM)
```
GEM_API_KEY=*** (ver .env.master)
```

### QuickBooks (de MCP - MULTIPLAS EMPRESAS)
```
QUICKBOOKS_CLIENT_ID=*** (ver .env.master)
QUICKBOOKS_CLIENT_SECRET=*** (ver .env.master)
# Realms configurados: 1 sandbox + 7 production
```

---

## 5. Acessos Globais do Sistema

### Ferramentas Instaladas (do Toolkit Scan)
| Ferramenta | Versao | Acesso |
|------------|--------|--------|
| Claude Code CLI | 2.0.75 | Anthropic API |
| Tailscale | 1.88.1 | VPN (40+ machines) |
| Playwright | 1.56.0 | Browser automation |
| Git/GitHub | Latest | Repos publicos/privados |
| Node.js | Latest | Runtime para MCPs |
| Python | 3.x | Scripts e automacao |

### Claude Desktop Settings
- **bypassPermissions**: Habilitado
- **alwaysThinking**: Habilitado
- Tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Task, NotebookEdit

---

## 6. Recomendacoes

### Acao Imediata
1. Criar `.env.master` no SpineHUB com TODAS as credenciais consolidadas
2. Adicionar Desktop Commander MCP ao claude_desktop_config.json
3. Documentar MCPs no SpineHUB para referencia

### Acao Futura
4. Criar script de validacao de credenciais
5. Implementar rotacao automatica de tokens
6. Centralizar refresh de OAuth tokens

---

## 7. Arquivos de Referencia

| Arquivo | Localizacao |
|---------|-------------|
| MCP Config | C:\Users\adm_r\AppData\Roaming\Claude\claude_desktop_config.json |
| TSA_CORTEX .env | C:\Users\adm_r\Projects\TSA_CORTEX\.env |
| SLACK_MONITOR .env | C:\Users\adm_r\SLACK_MONITOR\.env |
| GEM-BOOM .env | C:\Users\adm_r\GEM-BOOM\.env |
| LINEAR_AUTO .env | C:\Users\adm_r\Projects\LINEAR_AUTO\.env |
| QBO WFS .env | C:\Users\adm_r\QBO WFS\.env |

---

**Conclusao**: SpineHUB tem a ESTRUTURA para todos os acessos, mas precisa das credenciais REAIS copiadas dos outros projetos. O sistema de MCPs e global e funciona para todos os projetos.
