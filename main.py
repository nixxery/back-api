import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from fpdf import FPDF
from yolo_func import *

app = Flask(__name__)

# Настройка CORS с явным указанием домена фронтенда
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://da-vinci-web.web.app",  # ← ДОБАВЬ ЭТОТ ДОМЕН
            "http://localhost:3000",
            "http://127.0.0.1:3000", 
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"]
    }
})

# Или САМЫЙ ПРОСТОЙ вариант - разрешить ВСЕ домены
# CORS(app)  # ← раскомментируй эту строку вместо верхней настройки

@app.route('/api/keypoints', methods=['POST', 'OPTIONS'])
@cross_origin()
def get_keypoints():
    # Обработка preflight запроса OPTIONS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'https://da-vinci-web.web.app')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200
        
    # Проверяем, что POST запрос содержит файл
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    # Проверяем, что файл имеет допустимое расширение
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        # Сохраняем файл во временную директорию
        filepath = os.path.join(os.getcwd(), file.filename)
        file.save(filepath)
        result = process_video(filepath, confidence_threshold=0.5)
        
        # Добавляем CORS заголовки к ответу
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', 'https://da-vinci-web.web.app')
        return response

    else:
        return jsonify({'error': 'File type not allowed'})

@app.route('/api/file', methods=['GET'])
@cross_origin()
def get_file():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Анализ видео", ln=1, align="C")
    pdf.cell(200, 10, txt=" ", ln=1, align="C")
    pdf.cell(200, 10, txt="Длина шага: ", ln=1, align="L")

    pdf_file_path = "simple_demo.pdf" 
    pdf.output(pdf_file_path, 'F') 

    return send_file(
        pdf_file_path,
        as_attachment=True,
        download_name="simple_demo.pdf",
        mimetype='application/pdf'
    )

# Health check endpoint
@app.route('/api/health', methods=['GET'])
@cross_origin()
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "YOLO Video Analysis API",
        "cors": "enabled",
        "frontend": "https://da-vinci-web.web.app"
    })

# Функция для проверки разрешенных расширений файлов
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
