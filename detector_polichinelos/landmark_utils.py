import math
import cv2

class PoseDetector:
    def __init__(self, ...):
        self.lm_list = []
        self.results = None

    # Função 1: Extrair Landmarks!

    def get_landmarks(self, img):
        """
        Extrai as coordenadas dos landmarks detectados pela última detecção.
        Converte as coordenadas normalizadas (0-1) em pixels.

        Args:
            img (np.array): Imagem atual do OpenCV.

        Returns:
            list: Lista de landmarks no formato [[id, x, y], ...].
                  Exemplo: [[0, 480, 320], [1, 490, 310], ...]
        """
        self.lm_list = []
        if self.results.pose_landmarks:
            h, w, _ = img.shape
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy])
        return self.lm_list

    # Função 2: Calcular Ângulo!

    def calculate_angle(self, lm_list, p1, p2, p3):
        """
        Calcula o ângulo entre três pontos (p1, p2, p3) a partir da lista de landmarks.

        Args:
            lm_list (list): Lista de landmarks no formato [[id, x, y], ...].
            p1, p2, p3 (int): IDs dos três pontos de referência.

        Returns:
            float: Ângulo em graus entre os três pontos.
        """
        if len(lm_list) == 0:
            return 0

        x1, y1 = lm_list[p1][1], lm_list[p1][2]
        x2, y2 = lm_list[p2][1], lm_list[p2][2]
        x3, y3 = lm_list[p3][1], lm_list[p3][2]

        angle = math.degrees(
            math.atan2(y3 - y2, x3 - x2) -
            math.atan2(y1 - y2, x1 - x2)
        )

        if angle < 0:
            angle += 360

        return angle
