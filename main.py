import os
from flask import Flask, request, jsonify, send_file
from yolo_func import *
from docxtpl import DocxTemplate
from docx2pdf import convert
from fpdf import FPDF

app = Flask(__name__)

@app.route('/api/keypoints', methods=['POST'])
def get_keypoints():
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
        return process_video(filepath, confidence_threshold=0.5)

    else:
        return jsonify({'error': 'File type not allowed'})



@app.route('/api/file', methods=['GET'])
def get_file():
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Times New Roman", "", "times.ttf", uni=True)
    pdf.set_font("Times New Roman", size=14)
    
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

# Функция для проверки разрешенных расширений файлов
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}  # Допустимые расширения файлов
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)