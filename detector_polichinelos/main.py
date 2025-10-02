import cv2
import time
from pose_detector import PoseDetector

def process_jumping_jack(detector, lm_list, stage, count):
    """
    Processa a lógica completa de contagem de polichinelos.
    Verifica simultaneamente: posição dos braços, abertura das pernas e movimento vertical (pulo).
    
    :param detector: Instância do PoseDetector (para cálculos de ângulos e distâncias)
    :param lm_list: Lista de landmarks detectados
    :param stage: Estado atual do movimento ("closed" ou "open")
    :param count: Contagem atual de polichinelos
    :return: Novo estágio e contagem atualizada
    """
    # Inicializa debug_info padrão
    debug_info = {
        'bracos_levantados': False,
        'pernas_abertas': False,
        'esta_no_ar': False,
        'distancia_tornozelos': 0,
        'distancia_quadris': 0
    }
    
    # Se não há landmarks detectados, retorna valores padrão
    if len(lm_list) == 0:
        return stage, count, debug_info
    
    # ============= LANDMARKS IMPORTANTES =============
    # Braços: 11=ombro_esq, 12=ombro_dir, 15=pulso_esq, 16=pulso_dir
    # Pernas: 23=quadril_esq, 24=quadril_dir, 27=tornozelo_esq, 28=tornozelo_dir
    # Corpo: 0=nariz (para detectar altura do pulo)
    
    # ============= 1. DETECÇÃO DOS BRAÇOS =============
    # Verifica se os braços estão levantados (pulsos acima dos ombros)
    pulso_esq_y = lm_list[15][2]
    pulso_dir_y = lm_list[16][2]
    ombro_esq_y = lm_list[11][2]
    ombro_dir_y = lm_list[12][2]
    
    # Braços considerados "levantados" quando ambos os pulsos estão acima dos ombros
    bracos_levantados = (pulso_esq_y < ombro_esq_y) and (pulso_dir_y < ombro_dir_y)
    
    # ============= 2. DETECÇÃO DA ABERTURA DAS PERNAS =============
    # Calcula a distância entre os tornozelos para medir abertura das pernas
    distancia_tornozelos = detector.calculate_distance(27, 28)  # tornozelo_esq para tornozelo_dir
    
    # Calcula a distância entre os quadris como referência (largura do corpo)
    distancia_quadris = detector.calculate_distance(23, 24)  # quadril_esq para quadril_dir
    
    # Pernas abertas: tornozelos estão significativamente mais afastados que os quadris
    # Fator de 1.8x foi escolhido empiricamente para detectar abertura adequada
    pernas_abertas = distancia_tornozelos > (distancia_quadris * 1.8)
    
    # ============= 3. DETECÇÃO DO MOVIMENTO VERTICAL (PULO) =============
    # Usa a altura do nariz como referência para detectar elevação do corpo
    nariz_y = lm_list[0][2]
    
    # Armazena a altura inicial na primeira execução (baseline)
    if not hasattr(process_jumping_jack, 'baseline_y'):
        process_jumping_jack.baseline_y = nariz_y
    
    # Calcula o deslocamento vertical em relação ao baseline
    deslocamento_vertical = process_jumping_jack.baseline_y - nariz_y
    
    # Considera que há pulo se a pessoa subiu pelo menos 20 pixels
    # (ajuste este valor conforme necessário para sua câmera/distância)
    esta_no_ar = deslocamento_vertical > 20
    
    # Atualiza o baseline gradualmente para compensar movimentos da câmera ou da pessoa
    process_jumping_jack.baseline_y = process_jumping_jack.baseline_y * 0.95 + nariz_y * 0.05
    
    # ============= 4. MÁQUINA DE ESTADOS - CONTAGEM DO POLICHINELO =============
    # Estado "closed": posição inicial/final (braços abaixados, pernas juntas)
    # Estado "open": posição aberta (braços levantados, pernas abertas, no ar)
    
    # Transição: closed -> open
    # Conta como "aberto" quando TODOS os critérios são satisfeitos simultaneamente
    if stage == "closed":
        if bracos_levantados and pernas_abertas and esta_no_ar:
            stage = "open"
    
    # Transição: open -> closed
    # Conta um polichinelo completo quando a pessoa retorna à posição fechada
    elif stage == "open":
        # Verifica se voltou para a posição fechada (braços abaixados E pernas juntas)
        bracos_abaixados = (pulso_esq_y > ombro_esq_y) and (pulso_dir_y > ombro_dir_y)
        pernas_juntas = distancia_tornozelos < (distancia_quadris * 1.5)
        
        if bracos_abaixados and pernas_juntas:
            count += 1  # Incrementa o contador
            stage = "closed"
    
    # ============= 5. RETORNA INFORMAÇÕES DE DEBUG =============
    # Retorna também informações adicionais para exibição na tela
    debug_info = {
        'bracos_levantados': bracos_levantados,
        'pernas_abertas': pernas_abertas,
        'esta_no_ar': esta_no_ar,
        'distancia_tornozelos': int(distancia_tornozelos),
        'distancia_quadris': int(distancia_quadris)
    }
    
    return stage, count, debug_info

def main():
    """
    Função principal que inicializa a webcam e executa o loop de detecção.
    """
    # Inicializa a captura de vídeo (0 = webcam padrão)
    cap = cv2.VideoCapture(0)
    pTime = 0
    
    # Cria instância do detector com confiança alta para melhor precisão
    detector = PoseDetector(detectionCon=0.7, trackCon=0.7)
    
    # Variáveis de contagem e controle de estado
    count = 0
    stage = "closed"  # Estado inicial: posição fechada
    
    print("=== CONTADOR DE POLICHINELOS ===")
    print("Instruções:")
    print("1. Fique de frente para a câmera")
    print("2. Certifique-se de que seu corpo inteiro está visível")
    print("3. Faça polichinelos completos: pule, abra braços E pernas simultaneamente")
    print("4. Pressione 'q' para sair\n")
    
    while True:
        success, img = cap.read()
        if not success:
            print("Erro: Não foi possível capturar a imagem da webcam.")
            break

        # Detecta a pose e desenha o esqueleto
        img = detector.find_pose(img)
        
        # Extrai os landmarks (sem desenhar círculos para não poluir a tela)
        lm_list = detector.find_landmarks(img, draw=False)
        
        # Processa a lógica de contagem do polichinelo
        stage, count, debug_info = process_jumping_jack(detector, lm_list, stage, count)
        
        # ============= INTERFACE VISUAL =============
        # Caixa preta no topo para informações principais
        cv2.rectangle(img, (0, 0), (400, 160), (0, 0, 0), -1)
        
        # Exibe a contagem em destaque
        cv2.putText(img, f'Polichinelos: {count}', (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        # Exibe o estado atual
        cor_estado = (0, 255, 0) if stage == "open" else (255, 255, 255)
        cv2.putText(img, f'Estado: {stage.upper()}', (10, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor_estado, 2)
        
        # ============= INDICADORES VISUAIS DE DEBUG =============
        # Mostra quais condições estão sendo atendidas
        y_pos = 150
        indicadores = [
            ('Bracos', debug_info['bracos_levantados']),
            ('Pernas', debug_info['pernas_abertas']),
            ('Pulo', debug_info['esta_no_ar'])
        ]
        
        for i, (nome, ativo) in enumerate(indicadores):
            cor = (0, 255, 0) if ativo else (100, 100, 100)
            cv2.putText(img, f'{nome}: {"OK" if ativo else "--"}', 
                       (10 + i*130, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2)
        
        # Exibe distâncias (útil para ajustar thresholds)
        cv2.putText(img, f'Dist. Pernas: {debug_info["distancia_tornozelos"]}px', 
                   (10, img.shape[0] - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Calcula e exibe FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, img.shape[0] - 20), 
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        # Mostra a janela com a imagem processada
        cv2.imshow("Contador de Polichinelos - Pressione 'q' para sair", img)
        
        # Aguarda tecla 'q' para encerrar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Libera recursos
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nPrograma encerrado. Total de polichinelos: {count}")

if __name__ == "__main__":
    main()