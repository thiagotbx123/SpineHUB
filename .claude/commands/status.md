# /status - Status do Projeto

Execute para obter visão geral do estado atual do projeto.

## O QUE VERIFICAR

### 1. Estado do Projeto
Leia `.claude/memory.md` e apresente:
- Fase atual
- Últimas ações realizadas
- Bloqueios conhecidos

### 2. Knowledge Base
Liste arquivos em `knowledge-base/`:
- Quantidade de documentos
- Última atualização

### 3. Sessões
Verifique `sessions/`:
- Total de sessões registradas
- Última sessão (data e resumo)

### 4. Git Status
Execute e apresente:
```bash
git status
git log --oneline -5
```

### 5. Próximas Ações
Baseado no contexto, sugira 3 próximas ações prioritárias.

---

## FORMATO DE SAÍDA

```
📊 STATUS DO PROJETO: [nome]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Fase Atual: [fase]
📅 Última Sessão: [data]
📚 Knowledge Base: [X] documentos
🔄 Git: [X] commits, branch [nome]

⚠️ Bloqueios:
- [bloqueio 1]
- [bloqueio 2]

✅ Últimas Ações:
- [ação 1]
- [ação 2]

🎯 Próximos Passos:
1. [ação prioritária 1]
2. [ação prioritária 2]
3. [ação prioritária 3]
```
