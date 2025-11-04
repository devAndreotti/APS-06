# 📁 Estrutura do Projeto

## 📊 Visão Geral

```
detector_polichinelos/
├── 📄 app.py                         # Aplicação Flask principal
├── 📄 contador.py                    # Detector para 1 pessoa
├── 📄 contador_multi.py              # Detector para 2 pessoas
├── 📄 requirements.txt               # Dependências Python
├── 📄 install.py                     # Script de instalação
│
├── 📁 static/                        # Todos os arquivos estáticos (CSS, JS, imagens)
│   ├── 📄 global.css                 # Estilos globais
│   ├── 📄 index.css                  # Estilos da página inicial
│   ├── 📄 contador.css               # Estilos do contador webcam
│   ├── 📄 contador_video.css         # Estilos do contador de vídeo
│   ├── 📄 script.js                  # JavaScript da aplicação
│   │
│   └── 📁 images/                    # Todas as imagens
│       ├── 📁 icons/                 # Ícones SVG (13 arquivos)
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
│       ├── 📁 backgrounds/           # Imagens de fundo
│       │   ├── back (1).webp
│       │   ├── back (2).webp
│       │   └── back (3).webp
│       │
│       └── 📁 project/               # Imagens do projeto
│           └── 1.png +
│
├── 📁 templates/                     # Templates HTML (Jinja2)
│   ├── index.html                     # Página inicial
│   ├── contador.html                  # Contador webcam
│   ├── contador_multi.html            # Contador 2 pessoas
│   └── contador_video.html            # Contador de vídeo
│
├── 📁 uploads/                        # Vídeos enviados pelos usuários
│   └── *.mp4             
│
├── 📁 tests/                          # Testes automatizados
│   ├── performance_test.py
│   ├── 📁 reports/                    # Relatórios gerados
│   └── USAGE.md
│
├── 📁 venv/                           # ⚠️ Ambiente virtual Python (sem subir no GitHub)
├── 📁 __pycache__/                    # ⚠️ Cache Python
└── 📁 .pytest_cache/                  # ⚠️ Cache pytest
```

## 📝 Detalhamento das Pastas

### ✅ **static/** - Arquivos estáticos (frontend)
**Propósito:** CSS, JavaScript, imagens  
**Organização:**
- `images/icons/` - Ícones SVG locais (sem dependências da internet)
- `images/backgrounds/` - Imagens de fundo
- `images/project/` - Imagens do projeto
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