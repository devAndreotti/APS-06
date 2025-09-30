# Checklist de Desenvolvimento - Detector de Polichinelos

Este checklist serve como um guia para acompanhar o progresso do desenvolvimento do projeto de detecção e contagem de polichinelos. Marque cada item como concluído (`[x]`) à medida que avança.

## 1. Configuração do Ambiente

- [ ] Criar diretório do projeto: `mkdir projeto_polichinelos`
- [ ] Navegar para o diretório do projeto: `cd projeto_polichinelos`
- [ ] Criar ambiente virtual Python: `python3.11 -m venv venv`
- [ ] Ativar ambiente virtual: `source venv/bin/activate` (Linux/macOS) ou `.\venv\Scripts\activate` (Windows)
- [ ] Instalar bibliotecas essenciais: `pip install mediapipe opencv-python numpy`

## 2. Implementação da Classe `PoseDetector`

- [ ] Definir a classe `PoseDetector` em um arquivo Python (ex: `pose_detector.py`)
- [ ] Implementar o método `__init__(self, ...)` para inicializar o modelo MediaPipe Pose.
- [ ] Implementar o método `find_pose(self, img, draw=True)` para processar frames e desenhar landmarks.
- [ ] Implementar o método `find_landmarks(self, img, draw=True)` para extrair coordenadas dos landmarks.
- [ ] Implementar o método `calculate_angle(self, p1, p2, p3)` para calcular ângulos entre landmarks.

## 3. Lógica de Contagem de Polichinelos

- [ ] Definir variáveis de estado para a contagem (ex: `count`, `stage`).
- [ ] Integrar a lógica de cálculo de ângulos dentro do loop de processamento de vídeo.
- [ ] Implementar a máquina de estados para detectar transições `DOWN` -> `UP` -> `DOWN`.
- [ ] Ajustar os limiares de ângulo para a detecção precisa dos estados `UP` e `DOWN`.
- [ ] Incrementar o contador de polichinelos na transição correta.

## 4. Aplicação Principal (`main.py`)

- [ ] Criar o arquivo `main.py`.
- [ ] Importar a classe `PoseDetector`.
- [ ] Implementar a função `main()` para orquestrar a aplicação.
- [ ] Inicializar a captura de vídeo (webcam ou arquivo).
- [ ] Criar uma instância de `PoseDetector`.
- [ ] Implementar o loop principal para ler frames, processar com `PoseDetector` e exibir resultados.
- [ ] Adicionar exibição visual da contagem na tela usando `cv2.putText`.
- [ ] Adicionar funcionalidade para sair do loop (ex: tecla 'q').

## 5. Funcionalidades Adicionais e Aprimoramentos

- [ ] **Processamento de Vídeo Gravado**: Adicionar funcionalidade para carregar e processar arquivos de vídeo.
- [ ] **Suporte a Múltiplas Pessoas**: Adaptar a lógica para detectar e contar polichinelos de múltiplas pessoas.
- [ ] **Melhoria da Precisão (Opcional)**:
    - [ ] Implementar calibração inicial para os ângulos.
    - [ ] Aplicar suavização de movimentos (ex: média móvel, filtro de Kalman).
    - [ ] Fornecer feedback de qualidade do exercício ao usuário.
- [ ] **Interface Gráfica (Opcional)**: Integrar com `Tkinter`, `PyQt` ou `Streamlit` para uma interface mais amigável.

## 6. Testes e Refinamento

- [ ] Realizar testes com diferentes cenários (iluminação, pessoas, velocidades de movimento).
- [ ] Refinar os limiares de ângulo e a lógica de estado para maior precisão.
- [ ] Otimizar o desempenho para processamento em tempo real.
- [ ] Documentar o código com comentários claros.

## 7. Documentação e Entrega

- [ ] Atualizar o `README.md` do projeto com instruções de uso e informações relevantes.
- [ ] Preparar o relatório final do APS, incluindo a metodologia, implementação e resultados.
- [ ] Gravar vídeo demonstrativo do sistema em funcionamento.

