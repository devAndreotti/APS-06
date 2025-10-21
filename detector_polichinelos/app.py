from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from contador import processar_video
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

CALIBRAR = False
CURRENT_DATA = {
    'jumps': 0,
    'stage': 'Preparando',
    'fps': 0,
    'calibrated': False
}

def reset_data():
    """Reseta os dados para valores iniciais"""
    global CURRENT_DATA
    CURRENT_DATA = {
        'jumps': 0,
        'stage': 'Preparando',
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
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
            return jsonify({'success': True, 'filename': file.filename})
        # Caso contrário, redirecionar (form tradicional)
        return redirect(url_for('contador_video', video=file.filename))
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
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
        if isinstance(data, dict) and 'jumps' in data and data['jumps'] >= 0:
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

if __name__ == '__main__':
    app.run(debug=True)
