import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
import uuid
from font_processor import process_font  # Asegúrate de tener este archivo
from flask_cors import CORS  # Importamos flask_cors

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-secret")

# Habilitamos CORS para todas las rutas
CORS(app)

# Create upload and processed folders if they don't exist
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # Opcional, si tienes una plantilla

@app.route('/upload', methods=['POST'])
def upload_font():
    if 'fontFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    font_file = request.files['fontFile']

    if font_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Verificar extensión del archivo
    filename = font_file.filename
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext not in ['.otf', '.ttf']:
        return jsonify({'error': 'Only .otf and .ttf files are allowed'}), 400

    # Generar nombre único para evitar colisiones
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    try:
        # Guardar el archivo subido
        font_file.save(upload_path)
        logger.debug(f"File saved to {upload_path}")

        # Obtener nombre original (opcional)
        original_filename = os.path.basename(font_file.filename)
        original_name, _ = os.path.splitext(original_filename)

        # Procesar la fuente
        output_path = process_font(upload_path, PROCESSED_FOLDER)

        if output_path is None:
            return jsonify({'error': 'Failed to process font file'}), 500

        processed_filename = os.path.basename(output_path)

        return jsonify({
            'success': True,
            'message': 'Font processed successfully!',
            'filename': processed_filename,
            'originalName': original_name
        })

    except Exception as e:
        logger.error(f"Error processing font: {str(e)}")
        return jsonify({'error': f'Error processing font: {str(e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    if not os.path.exists(os.path.join(PROCESSED_FOLDER, filename)):
        logger.error(f"File not found: {filename}")
        return jsonify({'error': 'File not found'}), 404

    original_name = filename
    if not filename.startswith("Not with my"):
        original_name = f"Not with my {filename}"

    logger.debug(f"Sending file: {filename} with download name: {original_name}")

    return send_from_directory(
        directory=PROCESSED_FOLDER,
        path=filename,
        as_attachment=True,
        download_name=original_name
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
