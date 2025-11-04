# Guia de Uso - Testes de Performance

Sistema automatizado de análise de performance para a aplicação web de detecção de polichinelos.

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.8+
- OpenCV, MediaPipe instalados
- Servidor Flask rodando na porta 5000 (para testes)
- Navegador Chromium instalado (para testes)

### Instalação das Dependências
```bash
# Instalar bibliotecas necessárias
pip install playwright psutil matplotlib opencv-python mediapipe

# Instalar navegador Chromium
python -m playwright install chromium
```

### Execução dos Testes

#### 1. Teste de Rede e Memória (Frontend)
```bash
# 1. Iniciar o servidor Flask (em outro terminal)
python app.py

# 2. Executar os testes
cd tests
python performance_test.py
```

## 📁 Relatórios Gerados

### Localização
Todos os relatórios são salvos na pasta `tests/reports/`: