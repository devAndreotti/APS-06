import time
from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from contador import processar_video
from contador_multi import ContadorPolichinelos
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

CALIBRAR = False
CURRENT_DATA = {
    'jumps': 0,
    'stage': 'down',
    'fps': 0,
    'calibrated': False
}

def reset_data():
    """Reseta os dados para valores iniciais"""
    global CURRENT_DATA
    CURRENT_DATA = {
        'jumps': 0,
        'stage': 'down',
        'fps': 0,
        'calibrated': False
    }

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contador', methods=['POST'])
def contador():
    reset_data()  # Resetar dados para nova sessão
    modo = request.form.get('modo')
    if modo == "arquivo":
        return redirect(url_for('contador_video'))
    
    return render_template('contador.html', modo=modo)



@app.route('/contador_video')
def contador_video():
    video_path = request.args.get('video')
    if video_path:
        reset_data()  # Resetar dados quando um novo vídeo é carregado
    return render_template('contadorVideo.html', video_path=video_path)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    file = request.files['video']
    if file and file.filename.endswith('.mp4'):
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(save_path)
        print(f"vídeo salvo em: {save_path}")
        reset_data()  # Resetar dados para o novo vídeo
        # Se for uma requisição AJAX (fetch), retornar JSON
        # .best verifica se application/json é a PRIMEIRA prioridade no Accept header
        is_ajax = request.accept_mimetypes.best == 'application/json'
        if is_ajax:
            return jsonify({'success': True, 'filename': file.filename})
        # Caso contrário, redirecionar (form tradicional)
        return redirect(url_for('contador_video', video=file.filename))
    else:
        is_ajax = request.accept_mimetypes.best == 'application/json'
        if is_ajax:
            return jsonify({'success': False, 'error': 'Arquivo inválido'}), 400
        return "Envie um arquivo .mp4 válido.", 400

@app.route('/video_feed')
def video_feed():
    modo = request.args.get('modo', 'webcam')
    path = request.args.get('path')
    global CALIBRAR, CURRENT_DATA

    def calibrar_callback():
        global CALIBRAR
        state = CALIBRAR
        CALIBRAR = False
        return state

    def update_data_callback(data):
        global CURRENT_DATA
        # Só atualizar se os dados forem válidos e não negativos
        if isinstance(data, dict):
            CURRENT_DATA.update(data)

    if modo == 'arquivo' and path:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
        return Response(processar_video(video_path, calibrar_callback, update_data_callback),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    return Response(processar_video(0, calibrar_callback, update_data_callback),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/calibrar', methods=['POST'])
def calibrar():
    global CALIBRAR
    CALIBRAR = True
    return ('', 204)

@app.route('/reset', methods=['POST'])
def reset():
    """Rota para resetar dados"""
    reset_data()
    return "Dados resetados", 200

@app.route('/api/data')
def get_data():
    global CURRENT_DATA
    return jsonify(CURRENT_DATA)

# definir a variável global
CURRENT_DATA1 = {
    'pessoas': [
        {"jumps": 0, "stage": "down", "fps": 0},  # pessoa 1
        {"jumps": 0, "stage": "down", "fps": 0}   # pessoa 2
    ]
}

# Rota para exibir a página do contador multi
@app.route('/contador_multi', methods=['GET'])
def contador_multi():
    return render_template('contador_multi.html')

# Rota da API para enviar dados do contador multi
@app.route('/api/data_multi')
def get_data_multi():
    global CURRENT_DATA1
    return jsonify(CURRENT_DATA1)

# Streaming do vídeo para duas pessoas
@app.route('/video_feed_multi')
def video_feed_multi():
    global CALIBRAR, CURRENT_DATA1

    def calibrar_callback():
        global CALIBRAR
        state = CALIBRAR
        CALIBRAR = False
        return state

    def update_data_callback(data):
        global CURRENT_DATA1
        # Atualiza os dados das duas pessoas
        CURRENT_DATA1['pessoas'][0].update({
            "jumps": data.get('pessoa1', {}).get('count', 0),
            "stage": data.get('pessoa1', {}).get('stage', 'down'),
            "fps": data.get('fps', 0)
        })
        CURRENT_DATA1['pessoas'][1].update({
            "jumps": data.get('pessoa2', {}).get('count', 0),
            "stage": data.get('pessoa2', {}).get('stage', 'down'),
            "fps": data.get('fps', 0)
        })

    # Importa a função generator do contador_multi
    from contador_multi import processar_video as processar_video_multi

    return Response(
        processar_video_multi(0, calibrar_callback, update_data_callback),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':
    app.run(debug=True)


