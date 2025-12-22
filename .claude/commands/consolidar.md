# /consolidar - Consolidação de Sessão

Execute esta rotina ao FINAL de cada sessão de trabalho para preservar conhecimento.

## PASSOS OBRIGATÓRIOS

### PASSO 1: Análise da Sessão
Analise o que foi feito nesta sessão:
- Decisões tomadas
- Novos conhecimentos adquiridos
- Arquivos criados/modificados
- Problemas resolvidos
- Tarefas completadas
- Novas tarefas identificadas

### PASSO 2: Criar Arquivo de Sessão
Crie arquivo em `sessions/YYYY-MM-DD_HH-MM.md` usando o template `sessions/_template.md`

### PASSO 3: Atualizar Knowledge Base
Atualize os arquivos relevantes em `knowledge-base/`:
- Novos aprendizados
- Documentação de APIs/integrações
- Troubleshooting descoberto

### PASSO 4: Atualizar Memory
Atualize `.claude/memory.md` com:
- Estado atual do projeto
- Últimas ações realizadas
- Bloqueios conhecidos
- Próximos passos sugeridos

### PASSO 5: Commit e Push
Execute:
```bash
git add .
git commit -m "consolidar: [resumo breve da sessão]"
git push
```

### PASSO 6: Relatório Final
Apresente ao usuário:
- Resumo do que foi consolidado
- Arquivos atualizados
- Commit realizado
- Próximos passos sugeridos

---

**IMPORTANTE:** Esta rotina garante que nenhum conhecimento seja perdido entre sessões.
