# Guia Completo para Desenvolvimento de Detector de Polichinelos com MediaPipe

Este documento serve como um guia completo e detalhado para o desenvolvimento de um sistema de visão computacional para detecção e contagem de polichinelos, utilizando Python e a biblioteca MediaPipe. O objetivo é fornecer uma base sólida, desde a configuração do ambiente até a implementação de funcionalidades avançadas, com explicações visuais e exemplos de código.

## 1. Visão Geral do Projeto

O projeto consiste em criar uma aplicação capaz de analisar um fluxo de vídeo (de uma webcam ou arquivo) para identificar a pose de uma ou mais pessoas e contar o número de polichinelos que elas realizam. A aplicação deve ser robusta o suficiente para lidar com diferentes condições de iluminação e cenários com múltiplas pessoas.

### 1.1. Arquitetura do Sistema

A arquitetura do sistema pode ser visualizada no seguinte diagrama:

![Arquitetura do Sistema](https://private-us-east-1.manuscdn.com/sessionFile/PcwzacAh8N586CduHZqpvY/sandbox/KcUtlPXEncBmk7SiZJvggA-images_1759233648877_na1fn_L2hvbWUvdWJ1bnR1L3N5c3RlbV9hcmNoaXRlY3R1cmU.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvUGN3emFjQWg4TjU4NkNkdUhacXB2WS9zYW5kYm94L0tjVXRsUFhFbmNCbWs3U2laSnZnZ0EtaW1hZ2VzXzE3NTkyMzM2NDg4NzdfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzTjVjM1JsYlY5aGNtTm9hWFJsWTNSMWNtVS5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=ghqaQ-qfkhl6R-nRM6LSOQBpSG2uNmX8OpfqrrWI8CnkrCbK9D4zQACAxzFhy9UA5BaKxPNpeYaaLfUz56Nx4j73N-xie47Hlo10y-EX5hWy6Vc~ND0qq99NMmFfwaf5urq~PeQjR~t~U9fYf-jPNB7V-PNhNIysfzRK9dzBV4RMeBLFP4m47Fioc-JkQmICizf06GtJm8heUafn6sagvicYhas6W9U45KYPyoMKGZpmUlehD3Ic0jVv0-8sw7hPTlhzLV0m6OdHYmqqyMXrnzPPDM5LGI2MaQkDSEHwZiRTcr4mrtwcQSNu2C5pHcYHrkmTCi~nCdLqXQR3njH3YA__)

Este fluxo ilustra como a entrada de vídeo é processada, desde a captura do frame até a renderização do resultado final com a contagem de polichinelos.

## 2. Requisitos Técnicos

### 2.1. Linguagem e Bibliotecas

| Tecnologia | Versão/Descrição | Propósito no Projeto |
| :--- | :--- | :--- |
| **Python** | 3.8 ou superior | Linguagem principal de desenvolvimento. |
| **MediaPipe** | Última versão | Biblioteca de IA do Google para detecção de pose em tempo real. |
| **OpenCV** | Última versão | Para captura e manipulação de vídeo, e para desenhar na tela. |
| **NumPy** | Última versão | Para cálculos numéricos eficientes, especialmente com coordenadas. |
| **Matplotlib** | Opcional | Útil para visualização de dados e análises de movimento. |

### 2.2. Funcionalidades Essenciais

1.  **Detecção de Pose em Tempo Real**: Captura de vídeo da webcam e detecção contínua de landmarks corporais.
2.  **Processamento de Vídeo Gravado**: Capacidade de analisar arquivos de vídeo existentes.
3.  **Contagem Automática de Polichinelos**: Lógica para identificar e contar o exercício.
4.  **Feedback Visual**: Exibição da contagem e dos landmarks na tela.
5.  **Suporte a Múltiplas Pessoas**: Detecção e contagem para mais de uma pessoa simultaneamente.

## 3. Guia de Instalação e Configuração

### 3.1. Ambiente Virtual

É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Crie um diretório para o projeto
mkdir projeto_polichinelos
cd projeto_polichinelos

# Crie e ative o ambiente virtual
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate  # Windows
```

### 3.2. Instalação das Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias com um único comando:

```bash
pip install mediapipe opencv-python numpy
```

## 4. Estrutura do Código e Funções Essenciais

Uma abordagem orientada a objetos é recomendada para organizar o código. A classe principal, que podemos chamar de `PoseDetector`, será responsável por toda a lógica de detecção e contagem.

### 4.1. Classe `PoseDetector`

```python
import cv2
import mediapipe as mp
import numpy as np

class PoseDetector:
    def __init__(self, mode=False, upBody=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        """Inicializa o detector de pose com os parâmetros do MediaPipe."""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=mode,
                                        model_complexity=1 if upBody else 2,
                                        smooth_landmarks=smooth,
                                        min_detection_confidence=detectionCon,
                                        min_tracking_confidence=trackCon)
        self.mp_draw = mp.solutions.drawing_utils

    def find_pose(self, img, draw=True):
        """Encontra a pose em uma imagem e desenha os landmarks."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(img, self.results.pose_landmarks,
                                        self.mp_pose.POSE_CONNECTIONS)
        return img

    def find_landmarks(self, img, draw=True):
        """Extrai a posição dos landmarks."""
        self.lm_list = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lm_list

    def calculate_angle(self, p1, p2, p3):
        """Calcula o ângulo entre três pontos."""
        # Extrai as coordenadas dos landmarks
        x1, y1 = self.lm_list[p1][1:]
        x2, y2 = self.lm_list[p2][1:]
        x3, y3 = self.lm_list[p3][1:]

        # Calcula o ângulo
        angle = np.degrees(np.arctan2(y3 - y2, x3 - x2) -
                           np.arctan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360
        return angle
```

### 4.2. Lógica de Contagem de Polichinelos

A contagem de polichinelos é baseada em uma máquina de estados que transita entre as posições "baixo" (`DOWN`) e "cima" (`UP`).

#### Diagrama de Fluxo de Estados

![Fluxo de Estados](https://private-us-east-1.manuscdn.com/sessionFile/PcwzacAh8N586CduHZqpvY/sandbox/KcUtlPXEncBmk7SiZJvggA-images_1759233648879_na1fn_L2hvbWUvdWJ1bnR1L3N0YXRlX2Zsb3c.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvUGN3emFjQWg4TjU4NkNkdUhacXB2WS9zYW5kYm94L0tjVXRsUFhFbmNCbWs3U2laSnZnZ0EtaW1hZ2VzXzE3NTkyMzM2NDg4NzlfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzTjBZWFJsWDJac2IzYy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=FyFzz9Pso0dK8InJknPzK7ksnMG-HoLZi5qI6yk9xgjvSBUI2QnbA-6usPq9DemLmk9Xj6jWWAP8Ik7FtgrPTj3ZNSWWclnAh1sWdxfiXudB8fKua7qZO8g1NZpX~vAcvlIAZOpUOxm2rNnzlaDDfgjzbywQpVnIBTq0bfFFRX5COu31gxY61kpqcyuRuV4JEonHXWAHzoas8DCk8HnbsCLjQ~9A6QqHIk4Y47t7uceoPNRMs5N8O4NyXXUDKT4xiBuB7Ew-lYg9wdVBzD7-8OITL2NmFBDFS2FRfzfuSY04EPM87xSLgeTZAtJGaNZgJidvh~mzzGUfWtZUBs-MkA__)

#### Pseudocódigo da Lógica de Contagem

```python
# Dentro do loop principal de processamento de vídeo

# 1. Encontre a pose e os landmarks na imagem
img = detector.find_pose(img)
lm_list = detector.find_landmarks(img, draw=False)

if len(lm_list) != 0:
    # 2. Calcule os ângulos relevantes (ex: ombros e quadris)
    left_arm_angle = detector.calculate_angle(11, 13, 15) # Ombro, cotovelo, pulso
    right_arm_angle = detector.calculate_angle(12, 14, 16)
    left_leg_angle = detector.calculate_angle(23, 25, 27) # Quadril, joelho, tornozelo
    right_leg_angle = detector.calculate_angle(24, 26, 28)

    # 3. Verifique a posição dos braços e pernas para determinar o estado
    # (Estes valores de ângulo são exemplos e precisam ser ajustados)
    arms_up = left_arm_angle > 160 and right_arm_angle < 200
    legs_apart = left_leg_angle > 160 and right_leg_angle < 200

    # 4. Lógica da máquina de estados
    if stage == "DOWN":
        if arms_up and legs_apart:
            stage = "UP"
    elif stage == "UP":
        if not arms_up and not legs_apart:
            stage = "DOWN"
            count += 1

# 5. Exiba a contagem na tela
cv2.putText(img, f'Contagem: {count}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 5,
            (255, 0, 0), 5)
```

## 5. Considerações Avançadas

### 5.1. Suporte a Múltiplas Pessoas

Para detectar múltiplas pessoas, você precisará iterar sobre cada conjunto de `pose_landmarks` detectado pelo MediaPipe. A lógica de contagem precisará ser instanciada para cada pessoa, mantendo o estado e a contagem individualmente.

### 5.2. Melhorando a Precisão

*   **Calibração**: Permita que o usuário faça uma pose inicial para calibrar os ângulos e posições, tornando a detecção mais robusta a diferentes tipos de corpo.
*   **Suavização**: Utilize médias móveis ou filtros (como o filtro de Kalman) para suavizar os movimentos dos landmarks e evitar contagens falsas devido a movimentos bruscos.
*   **Feedback de Qualidade**: Forneça feedback ao usuário sobre a qualidade do exercício, como "levante mais os braços" ou "afaste mais as pernas", com base nos ângulos medidos.

## 6. Próximos Passos

1.  **Implementar a Classe `PoseDetector`**: Comece criando a classe e as funções para detecção de pose e landmarks.
2.  **Desenvolver a Lógica de Contagem**: Implemente a máquina de estados para a contagem de polichinelos, ajustando os ângulos e limiares com base em testes.
3.  **Criar a Aplicação Principal**: Desenvolva o loop principal que captura o vídeo, chama o detector e exibe os resultados.
4.  **Refinar e Testar**: Teste a aplicação com diferentes vídeos e pessoas para refinar a precisão da contagem.

Este guia fornece um roteiro completo para o seu projeto. Sinta-se à vontade para adaptá-lo e expandi-lo conforme suas necessidades.



## 7. Tabela de Funções e Métodos Essenciais

A tabela a seguir detalha as principais funções e métodos que você precisará implementar, organizados pela classe `PoseDetector` e pelo script principal da aplicação.

### 7.1. Classe `PoseDetector`

| Método | Descrição |
| :--- | :--- |
| `__init__(self, ...)` | Construtor da classe. Inicializa o modelo `mp.solutions.pose` com os parâmetros de configuração (modo, complexidade do modelo, suavização, confiança de detecção e rastreamento). |
| `find_pose(self, img, draw=True)` | Recebe um frame de imagem (`img`), converte para o formato RGB, processa com o MediaPipe para encontrar a pose e, opcionalmente, desenha os landmarks e conexões na imagem. Retorna a imagem com os desenhos. |
| `find_landmarks(self, img, draw=True)` | Extrai as coordenadas (x, y) de todos os landmarks detectados no frame e os armazena em uma lista (`self.lm_list`). As coordenadas são convertidas de proporções (0.0 a 1.0) para pixels. Retorna a lista de landmarks. |
| `calculate_angle(self, p1, p2, p3)` | Calcula o ângulo formado por três pontos (landmarks), identificados por seus IDs. Essencial para determinar a posição dos membros (ex: ângulo do cotovelo, joelho, ombro). Retorna o ângulo em graus. |

### 7.2. Script Principal (ex: `main.py`)

| Função | Descrição |
| :--- | :--- |
| `main()` | Função principal que orquestra a aplicação. Inicializa a captura de vídeo (webcam ou arquivo), cria uma instância da classe `PoseDetector` e executa o loop de processamento de vídeo. |
| _(Loop de Processamento)_ | Dentro de `main()`, este loop lê cada frame do vídeo, chama os métodos de `PoseDetector` para encontrar a pose e os landmarks, aplica a lógica de contagem de polichinelos e exibe o frame processado com a contagem na tela. |
| `process_jumping_jack(lm_list, stage, count)` | Uma função (ou lógica dentro do loop) que recebe a lista de landmarks, o estado atual (`stage`) e a contagem (`count`). Implementa a máquina de estados para verificar se um polichinelo foi concluído e atualiza o estado e a contagem. Retorna o novo estado e a nova contagem. |

