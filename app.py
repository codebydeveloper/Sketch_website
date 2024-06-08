from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sketch_image(image_path):
    img = cv2.imread(image_path)
    edges = cv2.Canny(img, 100, 200, 3, L2gradient=True)
    white_background = np.ones_like(img) * 255
    black_edges = cv2.bitwise_not(edges)
    black_edges_colored = cv2.cvtColor(black_edges, cv2.COLOR_GRAY2BGR)
    mask = edges > 0
    white_background[mask] = black_edges_colored[mask]
    sketch_path = 'static/sketch.png'
    cv2.imwrite(sketch_path, white_background)
    return sketch_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        sketch_path = sketch_image(filename)
        return render_template('result.html', original_image=filename, sketch_image=sketch_path)
    else:
        return 'File not allowed'

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
