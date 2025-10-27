# Detector Polichinelos - Instalação

## 🚀 Instalação Rápida

### Script com verificações
```bash
python install.py
```
## 📋 Instalação Manual

Se preferir fazer manualmente:

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar aplicação
python app.py
```

## 🌐 Como Usar

1. Execute um dos scripts de instalação acima
2. Ative o ambiente virtual
3. Execute `python app.py`
4. Abra http://localhost:5000 no navegador

## 🔧 Dependências Principais

- **Flask**: Framework web
- **MediaPipe**: Detecção de pose
- **OpenCV**: Processamento de vídeo
- **NumPy**: Processamento numérico

## ❓ Problemas Comuns

### Ambiente virtual já existe
O script completo (`install.py`) pergunta se você quer recriar o ambiente virtual.

### Porta já em uso
Se a porta 5000 estiver ocupada, o Flask tentará usar outra porta automaticamente.