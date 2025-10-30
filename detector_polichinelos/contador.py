import cv2
import mediapipe as mp
import time
import math


# Classe responsável por detectar a pose do corpo humano usando MediaPipe
class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose  # Módulo de pose do MediaPipe
        self.pose = self.mp_pose.Pose()  # Inicializa o modelo de detecção de pose
        self.mp_draw = mp.solutions.drawing_utils  # Utilitário para desenhar landmarks
        self.results = None  # Armazena o resultado da detecção atual

    # Detecta a pose em uma imagem
    def find_pose(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Converte para RGB (necessário para o MediaPipe)
        self.results = self.pose.process(img_rgb)  # Processa a imagem e detecta os pontos da pose
        if self.results.pose_landmarks and draw:
            # Estilos personalizados: linhas cinza e pontos brancos
            landmark_spec = self.mp_draw.DrawingSpec(color=(50, 50, 50), thickness=2, circle_radius=2)
            connection_spec = self.mp_draw.DrawingSpec(color=(200, 200, 200), thickness=2, circle_radius=2)
            self.mp_draw.draw_landmarks(
                img,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=landmark_spec,
                connection_drawing_spec=connection_spec,
            )
        return img  # Retorna a imagem processada (com ou sem desenho)

    # Retorna a lista de landmarks (pontos do corpo) com suas coordenadas na imagem
    def find_landmarks(self, img):
        lm_list = []
        if self.results and self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape  # Altura, largura e canais da imagem
                cx, cy = int(lm.x * w), int(lm.y * h)  # Converte coordenadas normalizadas para pixels
                lm_list.append([id, cx, cy])  # Adiciona o id e as coordenadas do ponto
        return lm_list  # Retorna a lista de landmarks


# Verifica se todos os índices necessários existem na lista de landmarks
def has_required_landmarks(lm_list, ids):
    return all(i < len(lm_list) for i in ids)


# Função que processa o movimento do polichinelo (jumping jack)
def process_jumping_jack(lm_list, stage, count, calib, img, last_valid_lm):
    required_ids = [11, 12, 15, 16, 23, 24, 27, 28]  # IDs dos pontos usados (ombros, punhos, quadris e tornozelos)

    # Se não há calibração, retorna imediatamente (não deveria acontecer mais)
    if calib is None:
        return stage, count, last_valid_lm

    # Se landmarks estiverem incompletos, tenta usar o último válido
    if not has_required_landmarks(lm_list, required_ids):
        if last_valid_lm is not None and has_required_landmarks(last_valid_lm, required_ids):
            lm_list = last_valid_lm
        else:
            return stage, count, last_valid_lm  # Sai se não houver dados válidos

    # Atualiza o último frame válido apenas se tiver todos os pontos necessários
    if has_required_landmarks(lm_list, required_ids):
        last_valid_lm = lm_list

    # Se não houver landmarks suficientes, não faz nada
    if len(lm_list) == 0 or len(lm_list) < 29:
        return stage, count, last_valid_lm

    # Captura coordenadas dos principais pontos do corpo
    pulso_esq = lm_list[15][1:]
    pulso_dir = lm_list[16][1:]
    ombro_esq = lm_list[11][1:]
    ombro_dir = lm_list[12][1:]
    tornozelo_esq = lm_list[27][1:]
    tornozelo_dir = lm_list[28][1:]
    quadril_esq = lm_list[23][1:]
    quadril_dir = lm_list[24][1:]

    # Calcula distâncias entre partes do corpo
    dist_quadris = math.dist(quadril_esq, quadril_dir)
    dist_tornozelos = math.dist(tornozelo_esq, tornozelo_dir)

    # Define uma altura mínima que o braço deve subir para contar como levantado
    altura_minima_braço = img.shape[0] * 0.10  # 10% da altura da imagem

    # Verifica se os braços estão levantados (pulsos acima dos ombros)
    bracos_levantados = (
        pulso_esq[1] < ombro_esq[1] - altura_minima_braço and
        pulso_dir[1] < ombro_dir[1] - altura_minima_braço
    )

    # Verifica se as pernas estão abertas com base na calibração
    pernas_abertas = dist_tornozelos > dist_quadris * calib["perna"]

    # Lógica de transição entre estágios do polichinelo
    if bracos_levantados and pernas_abertas:
        if stage == "down":  # Mudou para posição alta
            stage = "up"
    elif not bracos_levantados and not pernas_abertas:
        if stage == "up":  # Retornou à posição inicial → conta um polichinelo
            count += 1
            stage = "down"

    return stage, count, last_valid_lm


# Função principal que processa o vídeo e conta polichinelos em tempo real
def processar_video(video_source, calibrar_callback, update_data_callback=None):
    # Verifica se a fonte é um arquivo de vídeo ou uma câmera
    if isinstance(video_source, str) and video_source.endswith('.mp4'):
        cap = cv2.VideoCapture(video_source)  # Lê o vídeo
    else:
        cap = cv2.VideoCapture(0)  # Usa a webcam

    detector = PoseDetector()
    pTime = 0  # Tempo anterior (para cálculo de FPS)

    # Estados
    stage = "down"
    count = 0
    last_valid_lm = None
    calibrated = False
    calib = None

    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.find_pose(img)
        lm_list = detector.find_landmarks(img)

        # Força calibração padrão ANTES de qualquer processamento
        if not calibrated:
            calib = {"perna": 1.5}
            calibrated = True

        # Calibração manual (quando o callback é acionado)
        if calibrar_callback():
            if lm_list and len(lm_list) > 28:
                quadril_esq = lm_list[23][1:]
                quadril_dir = lm_list[24][1:]
                tornozelo_esq = lm_list[27][1:]
                tornozelo_dir = lm_list[28][1:]
                dist_quadris = math.dist(quadril_esq, quadril_dir)
                dist_tornozelos = math.dist(tornozelo_esq, tornozelo_dir)
                fator_perna = dist_tornozelos / dist_quadris * 1.5
                calib = {"perna": fator_perna}
                calibrated = True
                # print("Calibrado!")  # Debug removido

        # Processar contagem (agora calib nunca será None)
        stage, count, last_valid_lm = process_jumping_jack(
            lm_list, stage, count, calib, img, last_valid_lm
        )

        # Calcular FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if cTime != pTime else 0
        pTime = cTime

        # Enviar dados para o frontend
        if update_data_callback:
            update_data_callback({
                'jumps': count,
                'stage': stage,
                'fps': int(fps),
                'calibrated': calibrated
            })


        # Codificar o frame para o Flask (streaming)
        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
