# ESPINHA_DORSAL

Template de estrutura padrão para projetos com Claude Code.

## O que é

A **ESPINHA_DORSAL** é um conjunto de rotinas e estruturas que garantem:
- ✅ Persistência de contexto entre sessões
- ✅ Documentação automática de trabalho
- ✅ Versionamento com Git
- ✅ Qualidade de código (pre-commit hooks)
- ✅ Base de conhecimento organizada

## Como Aplicar em um Projeto

### Método 1: Copiar Estrutura
```bash
# Copie toda a estrutura para seu projeto
cp -r ESPINHA_DORSAL/.claude SEU_PROJETO/
cp -r ESPINHA_DORSAL/sessions SEU_PROJETO/
cp -r ESPINHA_DORSAL/knowledge-base SEU_PROJETO/
cp ESPINHA_DORSAL/CLAUDE.md SEU_PROJETO/
cp ESPINHA_DORSAL/.gitignore SEU_PROJETO/
cp ESPINHA_DORSAL/.pre-commit-config.yaml SEU_PROJETO/
```

### Método 2: Usar comando Claude
Diga ao Claude:
> "Aplique a ESPINHA_DORSAL no projeto [caminho]"

## Estrutura

```
ESPINHA_DORSAL/
├── .claude/
│   ├── commands/
│   │   ├── consolidar.md    # Rotina de fim de sessão
│   │   └── status.md        # Visão geral do projeto
│   ├── memory.md            # Estado persistente
│   └── settings.json        # Permissões
├── sessions/
│   ├── _template.md         # Template de sessão
│   └── README.md            # Instruções
├── knowledge-base/
│   └── README.md            # Instruções
├── CLAUDE.md                # Instruções obrigatórias
├── .gitignore               # Exclusões Git
├── .pre-commit-config.yaml  # Hooks de qualidade
└── README.md                # Este arquivo
```

## Comandos Disponíveis

| Comando | Quando Usar |
|---------|-------------|
| `/status` | Início de sessão ou quando precisar de visão geral |
| `/consolidar` | Final de sessão para documentar trabalho |

## Rotina de Trabalho

```
1. Início de Sessão
   └─> Claude lê memory.md automaticamente (via CLAUDE.md)

2. Durante o Trabalho
   └─> Trabalho normal, Claude mantém contexto

3. Fim de Sessão
   └─> Usuário executa /consolidar
       ├─> Documenta sessão
       ├─> Atualiza memory.md
       ├─> Cria arquivo em sessions/
       └─> Commit + Push Git
```

## Projetos Usando ESPINHA_DORSAL

- `intuit-boom` ✅
- `GEM-BOOM` ✅
- `QBO WFS` ⚠️ (parcial - falta Git e commands)

---

**Criado em:** 2024-12-22
**Versão:** 1.0
