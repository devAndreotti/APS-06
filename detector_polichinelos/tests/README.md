# Teste de Performance - Detector de Polichinelos

Sistema de análise de performance para a aplicação web de detecção de polichinelos.

## 🚀 Como Usar

### 1. Instalar Dependências
```bash
pip install playwright psutil
python -m playwright install chromium
```

### 2. Iniciar Servidor Flask
```bash
python app.py
```

### 3. Executar Teste
```bash
cd tests
python network_performance_test.py
```

## 📊 O que o Teste Faz

Navega automaticamente pelas páginas:
- `/index` - Página inicial
- `/contador` - Contador de polichinelos (webcam)
- `/contador_multi` - Contador para múltiplas pessoas
- `/contadorVideo` - Contador com vídeo carregado

## 📈 Métricas Coletadas

- **Tempo de carregamento** de cada página
- **Uso de memória** (média, pico, mínimo em MB)
- **Uso de CPU** (percentual médio)
- **Tráfego de rede** (dados baixados em KB/MB)
- **Número de requisições HTTP** por página
- **Tempo de carregamento do DOM**

## 📁 Relatórios Gerados

- **Terminal**: Tabela formatada durante execução
- **JSON**: `reports/network_memory_report.json`
- **HTML**: `reports/network_memory_report.html`
- **Gráfico**: `reports/performance_chart.png`

## 🔧 Solução de Problemas

- **Servidor não responde**: Verificar se `python app.py` está rodando
- **Erro de dependências**: Executar `pip install playwright psutil`
- **Navegador não encontrado**: Executar `python -m playwright install chromium`
- **Timeout**: Verificar se servidor está em `localhost:5000`

## 📋 Estrutura Final

```
tests/
├── network_performance_test.py    # Script principal
├── README.md                      # Esta documentação
└── reports/                       # Relatórios gerados
    ├── network_memory_report.json
    ├── network_memory_report.html
    └── performance_chart.png
```

**Sistema pronto para uso!** Execute `python network_performance_test.py` após instalar as dependências.