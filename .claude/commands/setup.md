# /setup - Configuracao Inicial do SpineHUB

Execute este comando quando um novo usuario estiver configurando o SpineHUB pela primeira vez.

## LOGICA DE DETECCAO

### PASSO 1: Verificar se usuario ja esta configurado
Verifique se existe o arquivo `.claude/user-config.md`:
- Se existir e estiver preenchido: Usuario ja configurado, mostrar boas-vindas
- Se nao existir ou estiver vazio: Iniciar onboarding

### PASSO 2: Onboarding Automatico
Tente detectar automaticamente:

```bash
# Nome e email do Git
git config user.name
git config user.email

# Sistema operacional
uname -a  # Linux/Mac
ver       # Windows

# Diretorio home
echo $HOME  # Linux/Mac
echo %USERPROFILE%  # Windows
```

### PASSO 3: Perguntar ao Usuario
Se nao conseguir detectar, pergunte:

1. **Nome completo**
2. **Email principal**
3. **Quais servicos usa?** (Slack, Linear, Drive, etc.)
4. **Idioma preferido para outputs**
5. **Projetos principais que vai trabalhar**

### PASSO 4: Criar Configuracao
1. Copiar `.claude/user-config.template.md` para `.claude/user-config.md`
2. Preencher com as informacoes coletadas
3. Verificar se `.env` existe (se necessario para APIs)
4. Testar conexoes basicas

### PASSO 5: Configurar Git (se necessario)
Se Git nao estiver configurado:
```bash
git config --global user.name "Nome do Usuario"
git config --global user.email "email@exemplo.com"
```

### PASSO 6: Verificar Estrutura SpineHUB
Confirmar que todos os diretorios existem:
- `.claude/` com commands e memory
- `sessions/`
- `knowledge-base/`
- `CLAUDE.md`

### PASSO 7: Mensagem de Boas-Vindas
Apresentar:
- Resumo da configuracao
- Comandos disponiveis (/status, /consolidar)
- Proximos passos sugeridos

---

## FORMATO DE SAIDA

```
╔══════════════════════════════════════════════════════════════╗
║           SpineHUB - Configuracao Inicial                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Usuario: [nome]                                             ║
║  Email: [email]                                              ║
║  Sistema: [OS]                                               ║
║                                                              ║
║  Servicos Detectados:                                        ║
║  ✅ Git configurado                                          ║
║  ⚠️  Slack (precisa configurar token)                        ║
║  ❌ Linear (nao configurado)                                 ║
║                                                              ║
║  Proximos Passos:                                            ║
║  1. Configure suas credenciais no .env                       ║
║  2. Execute /status para ver o estado atual                  ║
║  3. Use /consolidar ao final de cada sessao                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## TROUBLESHOOTING

| Problema | Solucao |
|----------|---------|
| Git nao instalado | Orientar instalacao do Git |
| Permissao negada | Verificar diretorios e .gitignore |
| .env nao existe | Criar template de .env |
| Conexao falhou | Verificar credenciais e internet |
