import cv2
import time
from pose_detector import PoseDetector

def process_jumping_jack(lm_list, stage, count):
    """
    Processa a lógica de contagem de polichinelos baseada nos landmarks detectados.
    
    Args:
        lm_list (list): Lista de landmarks do corpo (pontos com [id, x, y]).
        stage (str): Estado atual do movimento ("up" = braços levantados, "down" = braços abaixados).
        count (int): Número atual de polichinelos contados.
    
    Returns:
        tuple: (novo stage, nova contagem)
    """
    # Se nenhum ponto foi detectado, não faz nada
    if len(lm_list) == 0:
        return stage, count
    
    # Captura as posições verticais (eixo Y) dos pulsos e ombros
    # Quanto menor o valor de Y, mais "alto" está o ponto na tela
    # Landmarks usados (padrão MediaPipe Pose):
    # 11 = ombro esquerdo | 12 = ombro direito
    # 15 = pulso esquerdo | 16 = pulso direito
    pulso_esq_y = lm_list[15][2]
    pulso_dir_y = lm_list[16][2]
    ombro_esq_y = lm_list[11][2]
    ombro_dir_y = lm_list[12][2]
    
    # Verifica se os dois braços estão levantados (pulsos acima dos ombros)
    if pulso_esq_y < ombro_esq_y and pulso_dir_y < ombro_dir_y:
        # Se antes os braços estavam para baixo, muda o estado para "up"
        if stage == "down":
            stage = "up"
    
    # Verifica se os dois braços estão abaixados (pulsos abaixo dos ombros)
    if pulso_esq_y > ombro_esq_y and pulso_dir_y > ombro_dir_y:
        # Se antes estavam levantados, conta +1 polichinelo e volta para "down"
        if stage == "up":
            count += 1
            stage = "down"
    
    return stage, count


def main():
    # Inicializa captura da webcam (câmera 0 por padrão)
    cap = cv2.VideoCapture(0)
    
    # Variável auxiliar para cálculo de FPS
    pTime = 0
    
    # Inicializa o detector de pose (classe implementada em pose_detector.py)
    detector = PoseDetector()
    
    # Variáveis de contagem de polichinelos
    count = 0   # contador total
    stage = "down"  # estado inicial do movimento
    
    while True:
        # Lê o frame da webcam
        success, img = cap.read()
        if not success:
            print("Não foi possível capturar a imagem da webcam.")
            break

        # Detecta a pose no frame e desenha sobre a imagem
        img = detector.find_pose(img)
        
        # Extrai os landmarks do corpo (lista de pontos)
        lm_list = detector.find_landmarks(img, draw=False)
        
        # Processa a contagem de polichinelos com base nos landmarks
        stage, count = process_jumping_jack(lm_list, stage, count)
        
        # Caixa de fundo para informações
        cv2.rectangle(img, (0, 0), (350, 120), (0, 0, 0), -1)
        
        # Mostra a contagem de polichinelos
        cv2.putText(img, f'Polichinelos: {count}', (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        # Mostra o estado atual (up/down)
        cv2.putText(img, f'Estado: {stage}', (10, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Calcula FPS (frames por segundo)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (20, img.shape[0] - 20), 
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        # Exibe a janela com o vídeo processado
        cv2.imshow("Contador de Polichinelos", img)
        
        # Sai do loop ao pressionar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    # Libera recursos
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
