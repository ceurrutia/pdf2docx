from flask import Flask, request, jsonify, send_from_directory, render_template
from pdf2docx import Converter
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

#Definir rutas absolutas
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'converted')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convertir', methods=['POST'])
def convertir_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'El archivo debe ser un PDF'}), 400

    # Nombre seguro
    safe_filename = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    file.save(pdf_path)

    #Nombre de salida seguro con _ que sea seguro
    docx_filename = safe_filename.replace('.pdf', '.docx')
    docx_path = os.path.join(RESULT_FOLDER, docx_filename)

    print(f"Convirtiendo: {pdf_path} → {docx_path}")

    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return jsonify({'docx_url': f'/descargar/{docx_filename}'})
    except Exception as e:
        return jsonify({'error': f'Error al convertir: {str(e)}'}), 500

@app.route('/descargar/<filename>')
def descargar(filename):
    #Confirmo la arpeta de salida
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
