# Guia de Uso - Testes de Performance

Sistema automatizado de análise de performance para a aplicação web de detecção de polichinelos.

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.8+
- OpenCV, MediaPipe instalados
- Servidor Flask rodando na porta 5000 (para testes de rede)
- Navegador Chromium instalado (para testes de rede)

### Instalação das Dependências
```bash
# Instalar bibliotecas necessárias
pip install playwright psutil matplotlib opencv-python mediapipe

# Instalar navegador Chromium
python -m playwright install chromium
```

### Execução dos Testes

#### 1. Teste de Processamento de Vídeo (Backend)
```bash
cd tests
python video_processing_test.py [caminho_do_video]
# Exemplo: python video_processing_test.py ../uploads/WIN_20251021_17_26_30_Pro.mp4
```

#### 2. Teste de Rede e Memória (Frontend)
```bash
# 1. Iniciar o servidor Flask (em outro terminal)
python app.py

# 2. Executar os testes
cd tests
python network_performance_test.py
```

## 📊 Funcionalidades dos Testes

### 1. Teste de Processamento de Vídeo (`video_processing_test.py`)

Testa o **backend** de detecção de polichinelos:

#### Testes Incluídos
- ⏱️ **Performance de Frame** - Tempo de processamento por frame
- 🧠 **Vazamento de Memória** - Monitoramento durante streaming prolongado (60s)
- 👥 **Múltiplas Pessoas** - Comparação 1 pessoa vs 2 pessoas
- ⚡ **Uso de CPU** - Durante processamento de vídeo
- 🎯 **FPS Real** - Frames por segundo durante streaming

#### Métricas Coletadas
- **Tempo por Frame**: MediaPipe, encoding, captura
- **FPS**: Frames por segundo (média e variação)
- **Memória**: Uso durante processamento e crescimento
- **CPU**: Percentual durante processamento
- **Gargalos**: Identificação do componente mais lento

#### Como Interpretar
- **FPS > 25**: Performance excelente para tempo real
- **MediaPipe > 80%**: MediaPipe é o gargalo principal
- **Vazamento > 20MB**: Investigar cleanup de recursos
- **Impacto 2-pessoas > 30%**: Considerar otimizações

### 2. Teste de Rede e Memória (`network_performance_test.py`)

Testa o **frontend** e carregamento de páginas:

#### Páginas Testadas
- **Página Inicial** (`/`) - Seleção de modo de operação
- **Contador Individual** (`/contador`) - Detecção via webcam
- **Contador Múltiplo** (`/contador_multi`) - Detecção de múltiplas pessoas
- **Upload de Vídeo** (`/contador_video`) - Análise de arquivos MP4

#### Métricas Coletadas
- ⏱️ **Tempo de Carregamento** - Latência de cada página
- 🧠 **Uso de Memória** - Consumo RAM (média, pico, mínimo)
- ⚡ **Uso de CPU** - Percentual de processamento
- 🌐 **Tráfego de Rede** - Dados transferidos (KB/MB)
- 📡 **Requisições HTTP** - Número de chamadas por página
- 🎯 **Tempo DOM** - Carregamento do conteúdo

## 📁 Relatórios Gerados

### Localização
Todos os relatórios são salvos na pasta `tests/reports/`:

#### Testes de Vídeo
- **`video_processing_report.json`** - Dados brutos de performance de vídeo

#### Testes de Rede
- **`network_memory_report.json`** - Dados brutos em formato JSON
- **`network_memory_report.html`** - Relatório visual interativo
- **`performance_chart.png`** - Gráfico de tendências de performance

### Interpretação dos Resultados

#### Tempo de Carregamento
- **< 1s**: Excelente performance
- **1-3s**: Performance boa
- **3-5s**: Performance aceitável
- **> 5s**: Requer otimização

#### Uso de Memória
- **< 100MB**: Uso baixo
- **100-300MB**: Uso moderado
- **300-500MB**: Uso alto
- **> 500MB**: Requer investigação

## 🔧 Solução de Problemas

### Erros Comuns

#### Servidor não responde
```bash
# Verificar se Flask está rodando
curl http://localhost:5000
# Deve retornar HTML da página inicial
```

#### Dependências faltando
```bash
# Reinstalar dependências
pip install --upgrade playwright psutil matplotlib
python -m playwright install chromium
```

#### Timeout de conexão
- Verificar se servidor está em `localhost:5000`
- Verificar firewall/antivírus
- Testar com `curl http://localhost:5000`

#### Erro de encoding (Windows)
- O script já inclui correção automática para Windows
- Se persistir, executar: `chcp 65001` no terminal

## 📋 Estrutura do Projeto

```
tests/
├── video_processing_test.py       # Teste de performance de vídeo (backend)
├── network_performance_test.py    # Teste de performance de rede (frontend)
├── advanced_performance_test.py   # Testes avançados (acessibilidade, segurança)
├── USAGE.md                       # Este guia de uso
└── reports/                       # Relatórios gerados automaticamente
    ├── video_processing_report.json
    ├── network_memory_report.json
    ├── network_memory_report.html
    └── performance_chart.png
```

## 🎯 Casos de Uso

### Desenvolvimento
- Monitorar impacto de mudanças no código
- Identificar gargalos de performance
- Validar otimizações implementadas

### Produção
- Análise de performance em ambiente real
- Monitoramento de recursos do servidor
- Detecção de problemas de escalabilidade

### CI/CD
- Integração em pipelines de deploy
- Validação automática de performance
- Alertas de degradação de qualidade

## 📈 Interpretação Avançada

### Análise de Tendências
- **Crescimento linear**: Comportamento esperado
- **Picos abruptos**: Possível vazamento de memória
- **Degradação gradual**: Acúmulo de recursos

### Comparação de Páginas
- Identificar páginas mais pesadas
- Otimizar recursos críticos
- Balancear carga entre componentes

## 🎬 Exemplo de Execução Completa

### Passo a passo para testar tudo:

```bash
# 1. Testar backend de processamento de vídeo
cd tests
python video_processing_test.py ../uploads/WIN_20251021_17_26_30_Pro.mp4

# 2. (Em outro terminal) Iniciar servidor Flask
cd ..
python app.py

# 3. (Em outro terminal) Testar frontend
cd tests
python network_performance_test.py

# 4. Ver relatórios
ls -la reports/
```

## 🔍 Diferenças Entre os Testes

| Aspecto | Teste de Vídeo | Teste de Rede |
|---------|---------------|---------------|
| **Foco** | Backend (MediaPipe, OpenCV) | Frontend (HTML, CSS, JS) |
| **O que testa** | Processamento de frames | Carregamento de páginas |
| **Precisa Flask?** | ❌ Não | ✅ Sim |
| **Gargalos** | CPU, MediaPipe | Download, Renderização |
| **Quando usar** | Otimizar detecção | Otimizar interface |

---

**💡 Dica**: Execute ambos os testes para ter visão completa da performance do sistema!
