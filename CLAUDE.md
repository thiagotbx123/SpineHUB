# TSA SpineHub Consolidation - Instrucoes para Claude

> **LEITURA OBRIGATORIA** - Este arquivo contem instrucoes que o Claude DEVE seguir em TODA sessao.

---

## Protocolo de Inicio de Sessao

**ANTES de responder qualquer coisa, SEMPRE execute estes passos NA ORDEM:**

### 1. Detectar Usuario
Verifique se `.claude/user-config.md` existe:
- **Se NAO existir:** Execute `/setup` para configurar o novo usuario
- **Se existir:** Leia para conhecer o usuario e suas preferencias

### 2. Recuperar Contexto
Leia `.claude/memory.md` para entender:
- Fase atual do projeto
- Ultimas acoes realizadas
- Bloqueios conhecidos
- Proximos passos pendentes

### 3. Verificar Sessoes Anteriores
Verifique `sessions/` para:
- Ultima sessao registrada
- Trabalho recente nao consolidado
- Contexto adicional

### 4. Consultar Knowledge Base (se necessario)
Verifique `knowledge-base/` para:
- Documentacao de APIs
- Decisoes arquitetônicas
- Troubleshooting conhecido

---

## Protocolo de Novo Usuario

Se o usuario NAO estiver configurado (`.claude/user-config.md` nao existe):

1. **Tente detectar automaticamente:**
   ```bash
   git config user.name
   git config user.email
   ```

2. **Se conseguir:** Crie a configuracao com os dados detectados

3. **Se NAO conseguir:** Pergunte ao usuario:
   - Nome completo
   - Email
   - Quais servicos usa (Slack, Linear, Drive, etc.)
   - Idioma preferido

4. **Crie os arquivos necessarios** e oriente sobre proximos passos

---

## Protocolo de Fim de Sessao

**Ao finalizar trabalho, SEMPRE execute `/consolidar`:**

1. Documente o que foi feito
2. Atualize memory.md
3. Crie arquivo de sessao em `sessions/YYYY-MM-DD_HH-MM.md`
4. Commit e push para Git (se configurado)

---

## Comandos Disponiveis

| Comando | Funcao | Quando Usar |
|---------|--------|-------------|
| `/setup` | Configuracao inicial | Primeiro uso ou novo usuario |
| `/status` | Visao geral do projeto | Inicio de sessao |
| `/consolidar` | Salvar sessao | Final de cada sessao de trabalho |

---

## Regras de Ouro

1. **Detecte o usuario** - Sempre verifique user-config.md primeiro
2. **Nunca perca contexto** - Sempre leia memory.md
3. **Sempre documente** - Use /consolidar ao final
4. **Mantenha historico** - Nunca delete sessoes ou conhecimento
5. **Git e obrigatorio** - Todo trabalho deve ser versionado
6. **Oriente o usuario** - Se algo nao estiver configurado, ensine como fazer

---

## Estrutura do Projeto

```
SpineHUB/
├── .claude/
│   ├── commands/
│   │   ├── setup.md        # Configuracao inicial
│   │   ├── status.md       # Visao geral
│   │   └── consolidar.md   # Fim de sessao
│   ├── memory.md           # Estado persistente
│   ├── user-config.md      # Config do usuario (NAO COMMITAR)
│   ├── user-config.template.md  # Template para novos usuarios
│   └── settings.json       # Permissoes Claude
├── sessions/               # Historico de sessoes
├── knowledge-base/         # Base de conhecimento
├── .env                    # Credenciais (NAO COMMITAR)
├── .env.template           # Template de credenciais
├── CLAUDE.md               # Este arquivo
├── .gitignore              # Exclusoes Git
└── .pre-commit-config.yaml # Hooks de qualidade
```

---

## Arquivos Sensiveis (NAO COMMITAR)

Estes arquivos contem dados especificos do usuario e NAO devem ser versionados:

| Arquivo | Conteudo |
|---------|----------|
| `.claude/user-config.md` | Dados pessoais do usuario |
| `.env` | Credenciais e tokens |
| `*_secret*` | Qualquer arquivo com "secret" no nome |
| `*_token*` | Qualquer arquivo com "token" no nome |

---

## Fluxo de Trabalho

```
┌─────────────────────────────────────────────────────────────┐
│                      INICIO DE SESSAO                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ user-config.md  │
                    │    existe?      │
                    └─────────────────┘
                         │      │
                    NAO  │      │  SIM
                         ▼      ▼
              ┌──────────────┐  ┌──────────────┐
              │   /setup     │  │ Ler config   │
              │  (onboard)   │  │ do usuario   │
              └──────────────┘  └──────────────┘
                         │      │
                         └──────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Ler memory.md   │
                    │ e sessions/     │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │    TRABALHO     │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  /consolidar    │
                    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       FIM DE SESSAO                         │
└─────────────────────────────────────────────────────────────┘
```

---

**IMPORTANTE:** Estas instrucoes garantem continuidade, qualidade e portabilidade entre usuarios e sessoes.
