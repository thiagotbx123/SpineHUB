# Ferramentas de Refinamento de Codigo Python

> Guia completo das ferramentas integradas no SpineHUB para analise e refinamento de codigo.

---

## Resumo das Ferramentas

| Ferramenta | Funcao | O que Detecta |
|------------|--------|---------------|
| **Ruff** | Linter rapido | Style, imports, erros |
| **Bandit** | Seguranca | SQL injection, senhas hardcoded |
| **Vulture** | Dead code | Funcoes/variaveis nao usadas |
| **Radon** | Complexidade | Funcoes muito complexas |

---

## 1. RUFF - Linter Rapido

### O que e
Ruff e um linter Python extremamente rapido (10-100x mais rapido que flake8). Substitui flake8, isort, pyupgrade, e varios outros.

### Instalacao
```bash
pip install ruff
```

### O que detecta
| Codigo | Tipo | Exemplo |
|--------|------|---------|
| E*** | Erros de estilo | E501: linha muito longa |
| W*** | Warnings | W293: whitespace em branco |
| F*** | Pyflakes | F401: import nao usado |
| I*** | Imports | I001: imports desordenados |
| B*** | Bugbear | B006: argumento mutavel default |
| S*** | Seguranca | S101: uso de assert |

### Comandos
```bash
# Verificar erros
ruff check .

# Verificar e corrigir automaticamente
ruff check --fix .

# Formatar codigo (como black)
ruff format .

# Ver regras disponiveis
ruff rule --all

# Ignorar regra especifica
ruff check --ignore E501 .
```

### Configuracao (pyproject.toml)
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "S"]
ignore = ["E501"]  # ignorar linhas longas

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # permitir assert em testes
```

### Exemplo de Output
```
src/main.py:10:1: F401 [*] `os` imported but unused
src/main.py:25:5: E722 Do not use bare `except`
src/utils.py:15:1: I001 [*] Import block is un-sorted
```

---

## 2. BANDIT - Scanner de Seguranca

### O que e
Bandit encontra vulnerabilidades de seguranca comuns em codigo Python.

### Instalacao
```bash
pip install bandit
```

### O que detecta
| Codigo | Severidade | Vulnerabilidade |
|--------|------------|-----------------|
| B101 | LOW | Uso de assert |
| B105 | HIGH | Senha hardcoded |
| B106 | HIGH | Senha em argumento default |
| B301 | HIGH | Pickle inseguro |
| B302 | HIGH | Marshal inseguro |
| B602 | HIGH | subprocess com shell=True |
| B603 | HIGH | subprocess sem validacao |
| B608 | HIGH | SQL injection |

### Comandos
```bash
# Escanear diretorio
bandit -r .

# Formato JSON
bandit -r . -f json -o report.json

# Apenas alta severidade
bandit -r . -ll

# Excluir pastas
bandit -r . --exclude tests/,venv/

# Ignorar codigos especificos
bandit -r . --skip B101,B601
```

### Configuracao (.bandit)
```yaml
skips:
  - B101  # assert_used
  - B601  # paramiko_calls

exclude_dirs:
  - tests
  - venv
  - .venv
```

### Exemplo de Output
```
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password
   Severity: High   Confidence: Medium
   Location: config.py:25
   More Info: https://bandit.readthedocs.io/en/latest/plugins/b105

25      PASSWORD = "admin123"
```

---

## 3. VULTURE - Detector de Codigo Morto

### O que e
Vulture encontra codigo que nunca e usado: funcoes, classes, variaveis, imports.

### Instalacao
```bash
pip install vulture
```

### O que detecta
- Funcoes nao chamadas
- Classes nao instanciadas
- Variaveis nao utilizadas
- Imports nao usados
- Atributos nao acessados

### Comandos
```bash
# Escanear diretorio
vulture .

# Com confianca minima (0-100)
vulture --min-confidence 80 .

# Gerar whitelist de falsos positivos
vulture --make-whitelist . > whitelist.py

# Usar whitelist
vulture . whitelist.py

# Ordenar por confianca
vulture --sort-by-size .
```

### Whitelist (whitelist.py)
```python
# Falsos positivos - vulture vai ignorar
_.unused_function  # usado via reflection
_.MyClass.method   # chamado dinamicamente
```

### Exemplo de Output
```
src/utils.py:15: unused function 'old_helper' (90% confidence)
src/models.py:42: unused variable 'temp_data' (100% confidence)
src/main.py:8: unused import 'sys' (90% confidence)
```

---

## 4. RADON - Analisador de Complexidade

### O que e
Radon calcula metricas de complexidade do codigo, incluindo complexidade ciclomatica.

### Instalacao
```bash
pip install radon
```

### Metricas
| Metrica | Descricao |
|---------|-----------|
| CC | Complexidade Ciclomatica |
| MI | Indice de Manutenibilidade |
| Raw | LOC, comentarios, etc |
| Halstead | Metricas de Halstead |

### Escala de Complexidade
| Grade | Complexidade | Significado |
|-------|--------------|-------------|
| A | 1-5 | Simples, facil de manter |
| B | 6-10 | Baixa, aceitavel |
| C | 11-20 | Moderada, considerar refatorar |
| D | 21-30 | Alta, deve refatorar |
| E | 31-40 | Muito alta, urgente |
| F | 41+ | Extrema, reescrever |

### Comandos
```bash
# Complexidade ciclomatica
radon cc . -a

# Apenas funcoes complexas (C ou pior)
radon cc . -a -nc

# Formato JSON
radon cc . -j

# Indice de manutenibilidade
radon mi .

# Metricas raw (LOC, comentarios)
radon raw .

# Halstead metrics
radon hal .
```

### Exemplo de Output
```
src/process.py
    F 15:0 process_data - C (15)
    F 45:0 validate_input - B (8)
    F 78:0 export_results - A (3)

Average complexity: B (8.67)
```

---

## 5. USO INTEGRADO NO SPINEHUB

### Via Modulo Python
```python
from src.analyzers.code_analyzer import CodeAnalyzer

# Criar analisador
analyzer = CodeAnalyzer("/path/to/project")

# Verificar ferramentas disponiveis
tools = analyzer.check_tools()
print(tools)  # {'ruff': True, 'bandit': True, ...}

# Rodar todas as ferramentas
result = analyzer.run_all()
print(result.format_report())

# Rodar ferramenta especifica
ruff_result = analyzer.run_single("ruff")
print(f"Issues: {ruff_result.issue_count}")
```

### Via CLI (TODO)
```bash
# Futuro comando
spinehub analyze .
spinehub analyze --tool ruff .
spinehub analyze --fix .
```

---

## 6. WORKFLOW RECOMENDADO

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", ".bandit"]
```

### CI/CD Pipeline
```yaml
# .github/workflows/quality.yml
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Ruff Check
        run: ruff check .

      - name: Bandit Security
        run: bandit -r . -ll

      - name: Radon Complexity
        run: radon cc . -a -nc
```

### Ordem de Execucao
1. **Ruff** - Primeiro, corrige style e imports
2. **Vulture** - Remove codigo morto
3. **Bandit** - Verifica seguranca
4. **Radon** - Identifica funcoes para refatorar

---

## 7. INSTALACAO COMPLETA

```bash
# Todas as ferramentas
pip install ruff bandit vulture radon

# Verificar instalacao
ruff --version
bandit --version
vulture --version
radon --version
```

---

## 8. QUICK REFERENCE

### Comando Unico para Analise Completa
```bash
# Rodar tudo
ruff check . && bandit -r . -ll && vulture --min-confidence 80 . && radon cc . -a -nc
```

### Aliases Uteis (bash/zsh)
```bash
alias lint="ruff check --fix . && ruff format ."
alias security="bandit -r . -ll"
alias deadcode="vulture --min-confidence 80 ."
alias complexity="radon cc . -a -nc"
alias analyze="lint && security && deadcode && complexity"
```

---

## 9. PROBLEMAS COMUNS

### Ruff
| Problema | Solucao |
|----------|---------|
| Muitos erros E501 | Adicionar `ignore = ["E501"]` no config |
| Import nao reconhecido | Adicionar ao `[tool.ruff.lint.isort]` |

### Bandit
| Problema | Solucao |
|----------|---------|
| Falso positivo em teste | Usar `# nosec` no final da linha |
| Muitos B101 (assert) | Adicionar `--skip B101` |

### Vulture
| Problema | Solucao |
|----------|---------|
| Falso positivo | Criar whitelist.py |
| Confianca baixa | Usar `--min-confidence 90` |

### Radon
| Problema | Solucao |
|----------|---------|
| Funcao complexa | Dividir em funcoes menores |
| Grade F | Reescrever usando patterns |

---

**Versao:** 1.0
**Criado:** 2026-01-08
**SpineHUB:** v3.0
