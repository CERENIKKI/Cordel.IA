from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS  # Añadir esta línea
import os
import json
import uuid

app = Flask(__name__)
CORS(app)  # Esto habilita CORS para todas las rutas

# El resto de tu código sigue igual

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
DATA_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return '¡Servidor andando en Render!'

@app.route('/upload', methods=['POST'])
def upload_character():
    try:
        image = request.files['image']
        personality = request.form['personality']
        name = request.form['name']
        universe = request.form.get('universe', 'default')

        filename = secure_filename(image.filename)
        unique_id = str(uuid.uuid4())
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
        image.save(img_path)

        char_data = {
            'name': name,
            'personality': personality,
            'universe': universe,
            'image': img_path
        }

        with open(f"{DATA_FOLDER}/{unique_id}.json", "w") as f:
            json.dump(char_data, f)

        return jsonify({'status': 'ok', 'id': unique_id})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/character/<char_id>')
def get_character(char_id):
    try:
        with open(f"{DATA_FOLDER}/{char_id}.json") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    