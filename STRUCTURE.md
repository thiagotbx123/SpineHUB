# SpineHUB v3.0 - Estrutura Completa

> Documento canonico da estrutura e funcionalidades do SpineHUB

---

## 1. VISAO GERAL

**SpineHUB** e um toolkit de suporte para projetos Claude Code que fornece:
- Gestao centralizada de credenciais e MCPs
- Coleta de atividade de multiplas fontes (learning)
- Knowledge graph persistente
- Automacao de Git e versionamento
- Instalacao padronizada em qualquer projeto
- Sincronizacao de comandos entre projetos

---

## 2. ESTRUTURA DE DIRETORIOS

```
SpineHUB/
├── spinehub.py              # CLI PRINCIPAL (560+ linhas)
│
├── core/                    # NUCLEO DO SISTEMA
│   ├── commands/            # Slash commands (templates)
│   │   ├── setup.md         # /setup - Configuracao inicial
│   │   ├── status.md        # /status - Status do projeto
│   │   ├── consolidar.md    # /consolidar - Fim de sessao
│   │   └── learn.md         # /learn - Documentacao do learn
│   │
│   ├── scripts/             # Scripts de automacao
│   │   ├── install.py       # Instalar SpineHUB em projetos
│   │   ├── sync.py          # Sincronizar comandos
│   │   └── activate.py      # Ativacao global
│   │
│   └── templates/           # Templates para novos projetos
│       ├── CLAUDE.md.template
│       ├── memory.md.template
│       ├── session.md.template
│       ├── settings.json.template
│       └── gitignore.template
│
├── modules/                 # MODULOS FUNCIONAIS
│   ├── collectors/          # Sistema de coleta de atividade
│   │   ├── __init__.py      # Factory e runner
│   │   ├── base.py          # Classes base (ActivityEvent, etc)
│   │   ├── claude.py        # ClaudeCollector
│   │   ├── slack.py         # SlackCollector
│   │   └── local.py         # LocalCollector
│   │
│   ├── credentials/         # Gestao de credenciais
│   │   ├── __init__.py      # Package init
│   │   ├── manager.py       # CredentialsManager
│   │   └── validators.py    # Validadores de API
│   │
│   └── github/              # Operacoes Git
│       ├── __init__.py
│       └── git_manager.py   # GitManager (511 linhas)
│
├── src/                     # BIBLIOTECA SPINEHUB
│   ├── spinehub/            # Core do knowledge graph
│   │   ├── __init__.py
│   │   ├── core.py          # SpineHub class principal
│   │   ├── entities.py      # Entity, Relation, Artifact
│   │   ├── storage.py       # Persistencia JSON
│   │   └── benchmark.py     # Benchmarking
│   │
│   ├── analyzers/           # Analisadores de codigo
│   │   ├── __init__.py
│   │   ├── analyzer_base.py # Base class
│   │   └── code_analyzer.py # Ruff, Bandit, Vulture, Radon
│   │
│   └── cli.py               # CLI alternativo
│
├── credentials/             # CREDENCIAIS E AUDITORIA
│   ├── .env.template        # Template de credenciais
│   ├── ACCESS_AUDIT.md      # Auditoria de acessos
│   ├── README.md            # Documentacao
│   └── validate.py          # Script de validacao
│
├── data/                    # DADOS PERSISTENTES
│   └── spinehub.json        # Knowledge graph (entities, events)
│
├── projects/                # REGISTRO DE PROJETOS
│   └── registry.json        # Lista de projetos instalados
│
├── sessions/                # HISTORICO DE SESSOES
│   ├── _template.md
│   ├── 2025-12-22_*.md
│   └── 2026-01-08_*.md
│
├── knowledge-base/          # BASE DE CONHECIMENTO
│   ├── README.md
│   └── TOOLKIT_INSTALLATION_GUIDE.md
│
├── tests/                   # TESTES
│   └── test_spinehub.py
│
├── .claude/                 # CONFIG CLAUDE LOCAL
│   ├── commands/            # Slash commands ativos
│   ├── memory.md            # Estado persistente
│   ├── user-config.md       # Config do usuario
│   └── settings.json        # Permissoes
│
├── CLAUDE.md                # Instrucoes para Claude
├── README.md                # Documentacao geral
├── STRUCTURE.md             # Este arquivo
├── requirements.txt         # Dependencias Python
├── .env.master              # Credenciais consolidadas (gitignored)
└── .gitignore               # Exclusoes Git
```

---

## 3. COMANDOS CLI

### 3.1 spinehub init
Instala SpineHUB em qualquer projeto.

```bash
spinehub init                      # Diretorio atual
spinehub init /path/to/project     # Diretorio especifico
spinehub init --name "Meu Projeto" # Com nome
```

**O que faz:**
- Cria estrutura `.claude/` com commands, memory.md, settings.json
- Cria `sessions/` e `knowledge-base/`
- Cria `CLAUDE.md` com instrucoes
- Registra projeto em `projects/registry.json`

---

### 3.2 spinehub learn
Coleta atividade de multiplas fontes e alimenta o knowledge graph.

```bash
spinehub learn                     # Ultimos 7 dias, todas fontes
spinehub learn --days 30           # Ultimos 30 dias
spinehub learn --sources claude    # So Claude
spinehub learn --sources claude,slack,local
spinehub learn --dry-run           # Ver o que seria coletado
```

**Fontes disponiveis:**
| Fonte | O que coleta |
|-------|--------------|
| claude | ~/.claude/history.jsonl, sessions/*.jsonl, sessions/*.md |
| slack | DMs, mensagens de canais, mencoes (via API) |
| local | Arquivos modificados em ~/Downloads, ~/Documents |

**Output:**
- Eventos normalizados em `data/spinehub.json`
- Estatisticas de coleta

---

### 3.3 spinehub credentials
Gerencia credenciais e MCPs centralizados.

```bash
spinehub credentials status        # Ver todas credenciais e MCPs
spinehub credentials mcp           # Listar MCPs configurados
spinehub credentials validate      # Testar credenciais com APIs
spinehub credentials copy --target /path/to/project
spinehub credentials export        # Exportar como .env
```

**Credenciais gerenciadas:**
- Slack (Bot, User, MCP tokens)
- Linear (API Key)
- Google Drive (OAuth)
- GitHub (Token)
- Anthropic (API Key)
- Gem (API Key)
- QuickBooks (via MCPs)

---

### 3.4 spinehub git
Operacoes Git com automacao.

```bash
spinehub git status                # Status detalhado
spinehub git commit -m "msg"       # Commit com mensagem
spinehub git commit --auto         # Auto-generate message
spinehub git consolidar            # Commit de consolidacao
spinehub git push                  # Push
spinehub git pull                  # Pull
```

---

### 3.5 spinehub sync
Sincroniza comandos para todos os projetos registrados.

```bash
spinehub sync                      # Todos projetos
spinehub sync --project "Nome"     # Projeto especifico
spinehub sync --dry-run            # Ver o que seria sincronizado
```

---

### 3.6 spinehub activate
Instala SpineHUB globalmente para uso em qualquer projeto.

```bash
spinehub activate status           # Ver status
spinehub activate install          # Instalar globalmente
spinehub activate uninstall        # Remover
```

---

### 3.7 spinehub status
Mostra status do projeto atual.

```bash
spinehub status
```

---

### 3.8 spinehub list
Lista projetos registrados.

```bash
spinehub list
```

---

## 4. SLASH COMMANDS (CLAUDE)

### /setup
Configuracao inicial do usuario.
- Detecta usuario via `git config`
- Cria `.claude/user-config.md`
- Guia configuracao de credenciais

### /status
Visao geral do projeto.
- Fase atual
- Ultimas acoes
- Blockers
- Proximos passos

### /consolidar
Fim de sessao.
- Atualiza memory.md
- Cria arquivo em sessions/
- Commit e push Git

### /learn
Documentacao do comando learn (referencia).

---

## 5. MODULOS

### 5.1 Collectors (`modules/collectors/`)

**Base Classes:**
- `SourceSystem` - Enum: claude, slack, linear, drive, local
- `EventType` - Enum: message, file_created, file_modified, prompt, session
- `OwnershipType` - Enum: my_work, mentioned, context
- `ActivityEvent` - Evento normalizado com ID deterministico
- `CollectorResult` - Resultado de coleta
- `BaseCollector` - Classe abstrata

**ClaudeCollector:**
- Le `~/.claude/history.jsonl`
- Processa sessions em `~/.claude/projects/*/sessions/*.jsonl`
- Coleta markdown em `*/sessions/*.md`
- 92% noise reduction

**SlackCollector:**
- Three-pronged search: DMs, from:me, mentions
- Ownership classification
- Requer: SLACK_USER_TOKEN, SLACK_USER_ID

**LocalCollector:**
- Scan recursivo de diretorios
- SHA256 hashing para deduplicacao
- Denylist configuravel

---

### 5.2 Credentials (`modules/credentials/`)

**CredentialsManager:**
- Carrega de `.env.master`
- Valida com APIs
- Copia para outros projetos
- Gerencia MCPs

**Validators:**
- `validate_slack()` - Testa auth.test
- `validate_linear()` - Testa viewer query
- `validate_github()` - Testa /user endpoint
- `validate_google()` - Testa refresh token
- `validate_anthropic()` - Valida formato
- `validate_gem()` - Testa /candidates

---

### 5.3 GitHub (`modules/github/`)

**GitManager:**
- `get_status()` - Status do repo
- `add_all()` - Stage all changes
- `commit()` - Criar commit
- `auto_commit()` - Commit com mensagem automatica
- `consolidar_commit()` - Commit de consolidacao
- `push()` / `pull()` - Sync remoto
- `format_status_report()` - Report formatado

---

### 5.4 SpineHub Core (`src/spinehub/`)

**SpineHub (core.py):**
- Knowledge graph principal
- `add_entity()` - Adicionar entidade
- `add_relation()` - Adicionar relacao
- `add_artifact()` - Adicionar artefato
- `ingest_event()` - Ingerir ActivityEvent
- `query()` - Consultar grafo
- `save()` / `load()` - Persistencia

**Entities (entities.py):**
- `Entity` - Pessoa, projeto, ferramenta
- `Relation` - works_with, mentions, owns
- `Artifact` - Arquivo, documento
- `Pattern` - Padrao identificado

**Storage (storage.py):**
- Persistencia em JSON
- Backup automatico
- Merge de eventos

---

### 5.5 Analyzers (`src/analyzers/`)

**CodeAnalyzer:**
- Integra ruff, bandit, vulture, radon
- `analyze_file()` - Analisar arquivo
- `analyze_directory()` - Analisar diretorio
- `get_quality_score()` - Score de qualidade
- `format_report()` - Report formatado

---

## 6. MCPs CONFIGURADOS

| MCP | Funcao | Credencial |
|-----|--------|------------|
| filesystem | Acesso ao sistema de arquivos | - |
| memory | Knowledge graph persistente | - |
| github | GitHub API | GITHUB_PERSONAL_ACCESS_TOKEN |
| playwright | Automacao Chrome | - |
| slack | Slack API direto | SLACK_MCP_XOXC/XOXD |
| qb-* (8) | QuickBooks (8 empresas) | OAuth tokens |

---

## 7. CREDENCIAIS CONSOLIDADAS

Arquivo: `.env.master` (gitignored)

| Servico | Keys |
|---------|------|
| Slack | BOT_TOKEN, USER_TOKEN, USER_ID, MCP tokens |
| Linear | API_KEY, DEFAULT_TEAM |
| Google | CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN |
| GitHub | TOKEN |
| Anthropic | API_KEY |
| Gem | API_KEY |
| QuickBooks | CLIENT_ID, CLIENT_SECRET |

---

## 8. FLUXO DE USO

### Projeto Novo
```bash
cd /path/to/new/project
spinehub init --name "Meu Projeto"
```

### Sessao de Trabalho
```
1. Claude le CLAUDE.md automaticamente
2. Claude executa /status
3. Trabalho normal
4. Claude executa /consolidar
```

### Coleta de Conhecimento
```bash
spinehub learn --days 7
```

### Copiar Credenciais
```bash
spinehub credentials copy --target /path/to/project
```

---

## 9. INTEGRACAO COM OUTROS PROJETOS

SpineHUB pode ser "ativado" em qualquer projeto:

1. **Via instalacao**: `spinehub init`
2. **Via sync**: `spinehub sync`
3. **Via credentials**: `spinehub credentials copy`

Projetos registrados em `projects/registry.json`:
- TSA_CORTEX
- SLACK_MONITOR
- intuit-boom
- GEM-BOOM
- QBO WFS
- GOD_EXTRACT
- LINEAR_AUTO

---

## 10. ARQUIVOS IMPORTANTES

| Arquivo | Funcao |
|---------|--------|
| `spinehub.py` | CLI principal (560+ linhas) |
| `.env.master` | Todas credenciais |
| `data/spinehub.json` | Knowledge graph |
| `projects/registry.json` | Projetos registrados |
| `.claude/memory.md` | Estado persistente |
| `CLAUDE.md` | Instrucoes para Claude |

---

**Versao:** 3.0
**Atualizado:** 2026-01-08
