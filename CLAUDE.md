# Instruções para Claude - LEITURA OBRIGATÓRIA

> Este arquivo contém instruções que o Claude DEVE seguir em TODA sessão.

## Protocolo de Início de Sessão

**ANTES de responder qualquer coisa, SEMPRE:**

1. Leia `.claude/memory.md` para recuperar contexto
2. Verifique as últimas sessões em `sessions/`
3. Consulte `knowledge-base/` se necessário

## Protocolo de Fim de Sessão

**Ao finalizar trabalho, SEMPRE execute `/consolidar`:**

1. Documente o que foi feito
2. Atualize memory.md
3. Crie arquivo de sessão
4. Commit e push para Git

## Comandos Disponíveis

| Comando | Função |
|---------|--------|
| `/status` | Visão geral do estado do projeto |
| `/consolidar` | Consolidação de sessão (fim de trabalho) |

## Regras de Ouro

1. **Nunca perca contexto** - Sempre leia memory.md primeiro
2. **Sempre documente** - Use /consolidar ao final
3. **Mantenha histórico** - Nunca delete sessões ou conhecimento
4. **Git é obrigatório** - Todo trabalho deve ser versionado

## Estrutura do Projeto

```
projeto/
├── .claude/
│   ├── commands/       # Slash commands
│   ├── memory.md       # Estado persistente
│   └── settings.json   # Permissões
├── sessions/           # Histórico de sessões
├── knowledge-base/     # Base de conhecimento
├── CLAUDE.md           # Este arquivo
├── .gitignore          # Exclusões Git
└── .pre-commit-config.yaml  # Hooks de qualidade
```

---

**IMPORTANTE:** Estas instruções garantem continuidade e qualidade entre sessões.
