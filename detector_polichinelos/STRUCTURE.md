# 📁 Estrutura do Projeto

## 📊 Visão Geral

```
detector_polichinelos/
├── 📄 app.py                           # Aplicação Flask principal
├── 📄 contador.py                   # Detector para 1 pessoa
├── 📄 contador_multi.py         # Detector para 2 pessoas
├── 📄 requirements.txt            # Dependências Python
├── 📄 install.py                       # Script de instalação
│
├── 📁 static/                                  # Todos os arquivos estáticos (CSS, JS, imagens)
│   ├── 📄 global.css                      # Estilos globais
│   ├── 📄 index.css                       # Estilos da página inicial
│   ├── 📄 contador.css                  # Estilos do contador webcam
│   ├── 📄 contador_video.css       # Estilos do contador de vídeo
│   ├── 📄 script.js                         # JavaScript da aplicação
│   │
│   └── 📁 images/                         # Todas as imagens
│       ├── 📁 icons/                        # Ícones SVG (13 arquivos)
│       │   ├── activity.svg
│       │   ├── arrow-left.svg
│       │   ├── bar-chart-3.svg
│       │   ├── clock.svg
│       │   ├── file-video.svg
│       │   ├── info.svg
│       │   ├── play.svg
│       │   ├── play-circle.svg
│       │   ├── upload.svg
│       │   ├── user.svg
│       │   ├── users.svg
│       │   ├── video.svg
│       │   └── zap.svg
│       │
│       └── 📁 backgrounds/     # Imagens de fundo
│           ├── back (1).webp
│           ├── back (2).webp
│           ├── back (3).webp
│           └── Abstract Black.jpg
│
├── 📁 templates/                         # Templates HTML (Jinja2)
│   ├── index.html                         # Página inicial
│   ├── contador.html                    # Contador webcam
│   ├── contador_multi.html         # Contador 2 pessoas
│   └── contador_video.html         # Contador de vídeo
│
├── 📁 uploads/           # Vídeos enviados pelos usuários
│   └── *.mp4             
│
├── 📁 tests/                                              # Testes automatizados
│   ├── network_performance_test.py
│   ├── 📁 reports/                                    # Relatórios gerados
│   └── USAGE.md
│
├── 📁 venv/                           # ⚠️ Ambiente virtual Python (sem subir no GitHub)
├── 📁 __pycache__/              # ⚠️ Cache Python
└── 📁 .pytest_cache/             # ⚠️ Cache pytest
```

## 📝 Detalhamento das Pastas

### ✅ **static/** - Arquivos estáticos (frontend)
**Propósito:** CSS, JavaScript, imagens  
**Organização:**
- `images/icons/` - Ícones SVG locais (sem dependências da internet)
- `images/backgrounds/` - Imagens de fundo
- CSS modular por página
- JavaScript único para toda aplicação

### ✅ **templates/** - Templates HTML
**Propósito:** Páginas da aplicação web  
**Organização:**
- Cada template = uma rota da aplicação
- Usa Flask/Jinja2 para renderização

### ⚠️ **uploads/** - Vídeos temporários
**Propósito:** Armazenar vídeos enviados pelos usuários  
**⚠️ ATENÇÃO:**
- Pode conter arquivos grandes
- **NÃO fazer commit de vídeos reais para o git**
- Adicionar ao `.gitignore`

### ❌ **__pycache__/** e **.pytest_cache/** - Cache
**Pode apagar?** ✅ **SIM, sempre!**

**Por quê:**
- São gerados automaticamente pelo Python/pytest
- Não precisam estar no controle de versão
- Serão recriados quando necessário

**Comandos para limpar:**
```bash
# Windows PowerShell
Remove-Item -Recurse -Force __pycache__, .pytest_cache
```

### ❌ **venv/** - Ambiente Virtual
**Pode apagar?** ✅ **SIM (mas cuidado!)**

**Por quê:**
- É local e específico da sua máquina
- Pode ser regenerado com `pip install -r requirements.txt`

**⚠️ ATENÇÃO:**
- NÃO apague se você está usando o ambiente virtual atualmente
- Apague apenas se tiver certeza de que não precisa mais dele

## 🗑️ Sugestões de Melhoria

### 1. Criar `.gitignore`
```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg-info/
dist/
build/

# Virtual Environment
venv/
env/
ENV/

# Cache
.pytest_cache/
.cache/
*.cache

# Uploads (vídeos enviados pelos usuários)
uploads/*.mp4
uploads/*.avi
uploads/*.mov

# Mantém a pasta vazia
uploads/.gitkeep

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### 2. Estrutura de `static/` MELHORADA ✨
```
static/
├── css/
│   ├── global.css
│   ├── index.css
│   ├── contador.css
│   └── contador_video.css
├── js/
│   └── script.js
└── images/
    ├── icons/
    └── backgrounds/
```

### 3. Organizar `uploads/`
```bash
uploads/
├── temp/          # Vídeos temporários durante processamento
└── processed/     # Vídeos já processados (opcional)
```

## 🎯 Status Atual da Organização

| Pasta | Status | Nota |
|-------|--------|------|
| `static/images/icons/` | ✅ Organizado | Ícones SVG locais |
| `static/images/backgrounds/` | ✅ **RECÉM ORGANIZADO** | Imagens de fundo |
| `static/css/` | ⚠️ Ainda misturado | CSS na raiz de `static/` |
| `static/js/` | ⚠️ Ainda misturado | JS na raiz de `static/` |
| `templates/` | ✅ Organizado | HTML bem organizado |
| `uploads/` | ⚠️ Precisa `.gitignore` | Vídeos reais no git |
| `__pycache__/` | ❌ Cache | Pode apagar |
| `.pytest_cache/` | ❌ Cache | Pode apagar |

