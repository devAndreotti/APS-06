import cv2
import mediapipe as mp
import time
import math
    
class ContadorPolichinelos:
    def __init__(self):
        # Captura de vídeo padrão (câmera principal)
        self.cap = cv2.VideoCapture(0)

        # Inicializa o modelo de pose do MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_draw = mp.solutions.drawing_utils

        # Estado inicial de cada pessoa (para o modo 2 pessoas)
        # Armazena o estágio do movimento, contagem, últimos pontos válidos e calibração das pernas
        self.pessoa1 = {"stage": "down", "count": 0, "last_valid_lm": None, "calib": {"perna": 1.5}}
        self.pessoa2 = {"stage": "down", "count": 0, "last_valid_lm": None, "calib": {"perna": 1.5}}
        self.pTime = 0  # Para cálculo do FPS

    def reset_contadores(self):
        """Reseta os contadores e estados das duas pessoas"""
        self.pessoa1 = {"stage": "down", "count": 0, "last_valid_lm": None, "calib": {"perna": 1.5}}
        self.pessoa2 = {"stage": "down", "count": 0, "last_valid_lm": None, "calib": {"perna": 1.5}}

    def find_pose(self, img, draw=True):
        """
        Detecta a pose em uma imagem e desenha os pontos do corpo se 'draw' for True.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Converte para RGB (necessário para o MediaPipe)
        results = self.pose.process(img_rgb)  # Processa a imagem para detectar os marcos corporais
        if results.pose_landmarks and draw:
            # Desenha as conexões e pontos do corpo na imagem
            self.mp_draw.draw_landmarks(img, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        return img, results
    
    def find_landmarks(self, img, results):
        """
        Extrai as coordenadas (x, y) dos marcos (landmarks) detectados e retorna uma lista.
        """
        lm_list = []
        if results and results.pose_landmarks:
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)  # Converte coordenadas normalizadas para pixels
                lm_list.append([id, cx, cy])
        return lm_list

    def has_required_landmarks(self, lm_list, ids):
        """
        Verifica se todos os IDs necessários estão presentes na lista de landmarks.
        """
        return all(i < len(lm_list) for i in ids)

    def process_jumping_jack(self, lm_list, pessoa, img):
        """
        Analisa a pose para detectar e contar polichinelos de uma única pessoa.
        """
        required_ids = [11, 12, 15, 16, 23, 24, 27, 28]  # Pontos usados (ombros, pulsos, quadris e tornozelos)
        
        # Se não encontrou todos os pontos, usa os últimos válidos (caso disponíveis)
        if not self.has_required_landmarks(lm_list, required_ids):
            if pessoa["last_valid_lm"] is not None:
                lm_list = pessoa["last_valid_lm"]
            else:
                return pessoa  # Se não há pontos válidos, retorna sem atualizar nada

        pessoa["last_valid_lm"] = lm_list  # Armazena últimos pontos válidos

        if len(lm_list) == 0:
            return pessoa  # Evita erro caso não haja landmarks

        # Extrai coordenadas dos principais pontos do corpo
        pulso_esq = lm_list[15][1:]
        pulso_dir = lm_list[16][1:]
        ombro_esq = lm_list[11][1:]
        ombro_dir = lm_list[12][1:]
        tornozelo_esq = lm_list[27][1:]
        tornozelo_dir = lm_list[28][1:]
        quadril_esq = lm_list[23][1:]
        quadril_dir = lm_list[24][1:]

        # Calcula distâncias horizontais entre quadris e tornozelos
        dist_quadris = math.dist(quadril_esq, quadril_dir)
        dist_tornozelos = math.dist(tornozelo_esq, tornozelo_dir)

        # Determina o quanto o braço precisa subir para ser considerado "levantado"
        altura_minima_braço = img.shape[0] * 0.10
        bracos_levantados = (
            pulso_esq[1] < ombro_esq[1] - altura_minima_braço and
            pulso_dir[1] < ombro_dir[1] - altura_minima_braço
        )

        # Verifica se as pernas estão abertas com base na calibração da pessoa
        pernas_abertas = dist_tornozelos > dist_quadris * pessoa["calib"]["perna"]

        # Detecta o movimento completo (subir e descer)
        if bracos_levantados and pernas_abertas:
            if pessoa["stage"] == "down":  # Começou o movimento
                pessoa["stage"] = "up"
        elif not bracos_levantados and not pernas_abertas:
            if pessoa["stage"] == "up":  # Movimento completo -> conta 1 polichinelo
                pessoa["count"] += 1
                pessoa["stage"] = "down"

        return pessoa

    def processar_video(self, fonte, calibrar_callback, update_data_callback):
        """
        Lê o vídeo, processa em tempo real e envia frames com as contagens para o Flask.
        Suporta duas pessoas na mesma imagem (dividida ao meio).
        """
        cap = cv2.VideoCapture(fonte)
        # print("Modo 2 pessoas ativo!")  # Debug removido
        
        # Resetar contadores ao iniciar
        self.reset_contadores()

        while True:
            success, img = cap.read()
            if not success:
                break

            # Divide a imagem em duas metades (uma para cada pessoa)
            h, w, _ = img.shape
            metade1 = img[:, :w // 2]
            metade2 = img[:, w // 2:]

            # ---- Pessoa 1 ----
            metade1, results1 = self.find_pose(metade1)
            lm1 = self.find_landmarks(metade1, results1)
            if lm1:
                self.pessoa1 = self.process_jumping_jack(lm1, self.pessoa1, metade1)

            # ---- Pessoa 2 ----
            metade2, results2 = self.find_pose(metade2)
            lm2 = self.find_landmarks(metade2, results2)
            if lm2:
                self.pessoa2 = self.process_jumping_jack(lm2, self.pessoa2, metade2)

            # Junta as duas imagens novamente
            frame = cv2.hconcat([metade1, metade2])

            # Desenha linha branca divisória no meio
            cv2.line(frame, (w // 2, 0), (w // 2, h), (255, 255, 255), 2)

            # Calcula FPS (frames por segundo)
            cTime = time.time()
            fps = 1 / (cTime - self.pTime) if cTime != self.pTime else 0
            self.pTime = cTime

            # Envia dados atualizados (usado pelo Flask via callback)
            update_data_callback({
                "pessoa1": {
                    "count": self.pessoa1["count"],
                    "stage": self.pessoa1["stage"]
                },
                "pessoa2": {
                    "count": self.pessoa2["count"],
                    "stage": self.pessoa2["stage"]
                },
                "fps": int(fps)
            })

            # Codifica o frame como JPEG para transmissão
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Formata o frame no padrão multipart (para streaming via Flask)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        # Libera recursos ao encerrar
        cap.release()
        cv2.destroyAllWindows()


# Instância global (acessada pelo Flask)
contador = ContadorPolichinelos()

def processar_video(fonte, calibrar_callback, update_data_callback):
    """
    Função global de interface usada pelo Flask
    (chama internamente o método da instância 'contador').
    """
    return contador.processar_video(fonte, calibrar_callback, update_data_callback)