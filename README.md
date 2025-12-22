# TSA SpineHub Consolidation

Template de estrutura padrão para projetos com Claude Code.

## O que é

O **SpineHUB** é um conjunto de rotinas e estruturas que garantem:
- Persistencia de contexto entre sessoes
- Documentacao automatica de trabalho
- Versionamento com Git
- Qualidade de codigo (pre-commit hooks)
- Base de conhecimento organizada

## Como Aplicar em um Projeto

### Metodo 1: Copiar Estrutura
```bash
# Copie toda a estrutura para seu projeto
cp -r SpineHUB/.claude SEU_PROJETO/
cp -r SpineHUB/sessions SEU_PROJETO/
cp -r SpineHUB/knowledge-base SEU_PROJETO/
cp SpineHUB/CLAUDE.md SEU_PROJETO/
cp SpineHUB/.gitignore SEU_PROJETO/
cp SpineHUB/.pre-commit-config.yaml SEU_PROJETO/
```

### Metodo 2: Usar comando Claude
Diga ao Claude:
> "Aplique o SpineHUB no projeto [caminho]"

## Estrutura

```
SpineHUB/
├── .claude/
│   ├── commands/
│   │   ├── consolidar.md    # Rotina de fim de sessao
│   │   └── status.md        # Visao geral do projeto
│   ├── memory.md            # Estado persistente
│   └── settings.json        # Permissoes
├── sessions/
│   ├── _template.md         # Template de sessao
│   └── README.md            # Instrucoes
├── knowledge-base/
│   └── README.md            # Instrucoes
├── CLAUDE.md                # Instrucoes obrigatorias
├── .gitignore               # Exclusoes Git
├── .pre-commit-config.yaml  # Hooks de qualidade
└── README.md                # Este arquivo
```

## Comandos Disponiveis

| Comando | Quando Usar |
|---------|-------------|
| `/status` | Inicio de sessao ou quando precisar de visao geral |
| `/consolidar` | Final de sessao para documentar trabalho |

## Rotina de Trabalho

```
1. Inicio de Sessao
   └─> Claude le memory.md automaticamente (via CLAUDE.md)

2. Durante o Trabalho
   └─> Trabalho normal, Claude mantem contexto

3. Fim de Sessao
   └─> Usuario executa /consolidar
       ├─> Documenta sessao
       ├─> Atualiza memory.md
       ├─> Cria arquivo em sessions/
       └─> Commit + Push Git
```

## Projetos Usando SpineHUB

- `intuit-boom`
- `GEM-BOOM`
- `QBO WFS` (parcial)
- `TSA_CORTEX`

---

**Criado em:** 2024-12-22
**Versao:** 2.0 (renomeado de ESPINHA_DORSAL)
