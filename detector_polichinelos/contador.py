import cv2
import mediapipe as mp
import time
import math

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_pose(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(img, self.results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        return img

    def find_landmarks(self, img):
        lm_list = []
        if self.results and self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
        return lm_list

def process_jumping_jack(lm_list, stage, count, calib):
    if len(lm_list) == 0 or calib is None:
        return stage, count

    pulso_esq = lm_list[15][1:]
    pulso_dir = lm_list[16][1:]
    ombro_esq = lm_list[11][1:]
    ombro_dir = lm_list[12][1:]

    bracos_levantados = pulso_esq[1] < ombro_esq[1] and pulso_dir[1] < ombro_dir[1]

    tornozelo_esq = lm_list[27][1:]
    tornozelo_dir = lm_list[28][1:]
    quadril_esq = lm_list[23][1:]
    quadril_dir = lm_list[24][1:]

    dist_quadris = math.dist(quadril_esq, quadril_dir)
    dist_tornozelos = math.dist(tornozelo_esq, tornozelo_dir)
    pernas_abertas = dist_tornozelos > dist_quadris * calib["perna"]

    if bracos_levantados and pernas_abertas:
        if stage == "down":
            stage = "up"
    elif not bracos_levantados and not pernas_abertas:
        if stage == "up":
            count += 1
            stage = "down"

    return stage, count


def processar_video(modo, calibrar_callback):
    if modo == "arquivo":
        cap = cv2.VideoCapture("video.mp4")
    else:
        cap = cv2.VideoCapture(0)

    detector = PoseDetector()
    count = 0
    stage = "down"
    pTime = 0

    calibrated = False
    calib = None

    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.find_pose(img)
        lm_list = detector.find_landmarks(img)

        # Se o botão "Calibrar" for clicado (tava automatico)
        if calibrar_callback():
            if lm_list:
                quadril_esq = lm_list[23][1:]
                quadril_dir = lm_list[24][1:]
                tornozelo_esq = lm_list[27][1:]
                tornozelo_dir = lm_list[28][1:]
                dist_quadris = math.dist(quadril_esq, quadril_dir)
                dist_tornozelos = math.dist(tornozelo_esq, tornozelo_dir)
                fator_perna = dist_tornozelos / dist_quadris * 1.5
                calib = {"perna": fator_perna}
                calibrated = True
                print("Calibrado!")
        
        # Força calibração inicial
        if not calibrated:
            calib = {"perna": 1.5}
            calibrated = True

        # Processa contagem
        stage, count = process_jumping_jack(lm_list, stage, count, calib)

        # Desenho na tela
        cv2.rectangle(img, (0, 0), (400, 120), (0, 0, 0), -1)
        cv2.putText(img, f'Polichinelos: {count}', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(img, f'Estado: {stage}', (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        if not calibrated:
            cv2.putText(img, f'Pressione "Calibrar"', (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if cTime != pTime else 0
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (20, img.shape[0] - 20),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        # Envia frame pro navegador
        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
