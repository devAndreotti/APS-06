import cv2
import mediapipe as mp
import math

# Classe para detectar poses humanas usando MediaPipe
class PoseDetector:
    def __init__(self, mode=False, model_complexity=1, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        """
        Construtor da classe PoseDetector.
        Inicializa o modelo MediaPipe Pose com parâmetros de configuração.
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=mode,                # Se True, trata cada imagem de forma independente (sem rastrear sequência)
            model_complexity=model_complexity,     # Complexidade do modelo (0 = rápido, 1 = padrão, 2 = mais preciso)
            smooth_landmarks=smooth,               # Suavização dos landmarks (reduz "tremedeira" no vídeo)
            min_detection_confidence=detectionCon, # Confiança mínima para detectar uma pessoa
            min_tracking_confidence=trackCon       # Confiança mínima para rastrear a pose ao longo do tempo
        )

        # Ferramenta de desenho do MediaPipe (para landmarks e conexões)
        self.mp_draw = mp.solutions.drawing_utils
        # Guarda o resultado do processamento (pose detectada)
        self.results = None
        # Lista de landmarks do corpo em formato [id, x, y]
        self.lm_list = []

    # Função para detectar a pose em uma imagem
    def find_pose(self, img, draw=True):
        """
        Detecta a pose humana na imagem e opcionalmente desenha os landmarks.
        
        :param img: Frame de imagem no formato BGR (OpenCV)
        :param draw: Se True, desenha o esqueleto na imagem
        :return: Imagem com os landmarks desenhados
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Processa a imagem e obtém landmarks da pose
        self.results = self.pose.process(img_rgb)
        
        # Se a pose foi detectada e draw=True, desenha os landmarks e conexões na imagem
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(
                img,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS # conexões entre os pontos do corpo
            )
        return img

    # Função para extrair coordenadas dos landmarks
    def find_landmarks(self, img, draw=True):
        """
        Extrai as coordenadas (x, y) de todos os landmarks detectados.
        Converte coordenadas normalizadas (0-1) para pixels.
        
        :param img: Frame de imagem
        :param draw: Se True, desenha círculos nos landmarks
        :return: Lista de landmarks no formato [id, x, y]
        """
        self.lm_list = []
        # Se a pose foi detectada
        if self.results.pose_landmarks:
            h, w, _ = img.shape  # altura, largura da imagem
            # Percorre cada landmark detectado
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                # Converte coordenadas normalizadas (0-1) para pixels
                cx, cy = int(lm.x * w), int(lm.y * h)
                # Salva em lista no formato [id, x, y]
                self.lm_list.append([id, cx, cy])
                # Opcional: desenha um círculo em cada landmark
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return self.lm_list

    # Função para calcular ângulo entre três pontos do corpo (ex: braço, perna etc.)
    def calculate_angle(self, p1, p2, p3):
        # Se nenhum landmark foi detectado, retorna 0
        if len(self.lm_list) == 0:
            return 0
        
        # Extrai coordenadas (x, y) dos três pontos escolhidos
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        x3, y3 = self.lm_list[p3][1], self.lm_list[p3][2]
        
        # Calcula ângulo entre os vetores (p1->p2) e (p3->p2)
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - 
                           math.atan2(y1 - y2, x1 - x2))
        # Ajusta valores negativos para ficar no intervalo [0, 360]
        return angle + 360 if angle < 0 else angle

    def calculate_distance(self, p1, p2):
        """
        Calcula a distância euclidiana entre dois landmarks.
        Útil para medir abertura de pernas, distância entre mãos, etc.
        
        :param p1: ID do primeiro landmark
        :param p2: ID do segundo landmark
        :return: Distância em pixels
        """
        if len(self.lm_list) == 0:
            return 0
        
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance