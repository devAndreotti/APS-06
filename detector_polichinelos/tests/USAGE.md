# Guia de Uso - Testes de Performance

Sistema automatizado de análise de performance para a aplicação web de detecção de polichinelos.

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.8+
- Servidor Flask rodando na porta 5000
- Navegador Chromium instalado

### Instalação das Dependências
```bash
# Instalar bibliotecas necessárias
pip install playwright psutil matplotlib

# Instalar navegador Chromium
python -m playwright install chromium
```

### Execução
```bash
# 1. Iniciar o servidor Flask (em outro terminal)
python app.py

# 2. Executar os testes de performance
cd tests
python network_performance_test.py
```

## 📊 Funcionalidades do Teste

### Páginas Testadas
- **Página Inicial** (`/`) - Seleção de modo de operação
- **Contador Individual** (`/contador`) - Detecção via webcam
- **Contador Múltiplo** (`/contador_multi`) - Detecção de múltiplas pessoas
- **Upload de Vídeo** (`/contador_video`) - Análise de arquivos MP4

### Métricas Coletadas
- ⏱️ **Tempo de Carregamento** - Latência de cada página
- 🧠 **Uso de Memória** - Consumo RAM (média, pico, mínimo)
- ⚡ **Uso de CPU** - Percentual de processamento
- 🌐 **Tráfego de Rede** - Dados transferidos (KB/MB)
- 📡 **Requisições HTTP** - Número de chamadas por página
- 🎯 **Tempo DOM** - Carregamento do conteúdo

## 📁 Relatórios Gerados

### Localização
Todos os relatórios são salvos na pasta `tests/reports/`:

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
├── network_performance_test.py    # Script principal de testes
├── USAGE.md                       # Este guia de uso
└── reports/                       # Relatórios gerados automaticamente
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

---

**💡 Dica**: Execute os testes regularmente durante o desenvolvimento para manter a performance otimizada!
