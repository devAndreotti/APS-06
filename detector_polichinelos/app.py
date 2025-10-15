from flask import Flask, render_template, Response, request, redirect, url_for
from contador import processar_video
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

CALIBRAR = False

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contador', methods=['POST'])
def contador():
    modo = request.form.get('modo')
    if modo == "arquivo":
        return redirect(url_for('contador_video'))
    return render_template('contador.html', modo=modo)

@app.route('/contador_video')
def contador_video():
    return render_template('contadorVideo.html')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    file = request.files['video']
    if file and file.filename.endswith('.mp4'):
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(save_path)
        print(f"vídeo salvo em: {save_path}")
        return render_template('contadorVideo.html', video_path=file.filename)
    else:
        return "Envie um arquivo .mp4 válido.", 400

@app.route('/video_feed')
def video_feed():
    modo = request.args.get('modo', 'webcam')
    path = request.args.get('path')
    global CALIBRAR

    def calibrar_callback():
        global CALIBRAR
        state = CALIBRAR
        CALIBRAR = False
        return state

    if modo == 'arquivo' and path:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
        return Response(processar_video(video_path, calibrar_callback),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    return Response(processar_video(0, calibrar_callback),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/calibrar', methods=['POST'])
def calibrar():
    global CALIBRAR
    CALIBRAR = True
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
