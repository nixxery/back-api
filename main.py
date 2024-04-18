import pythoncom
import os
import sys
import stat
import argparse
import json
import concurrent.futures
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file
from ultralytics import YOLO
from yolo_func import *
from docxtpl import DocxTemplate
from docx2pdf import convert

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
    pythoncom.CoInitialize()
    doc = DocxTemplate("шаблон.docx")
    context = { 'size_of_step' : "48"}
    doc.render(context)
    doc.save("шаблон1.docx")
    convert("шаблон1.docx", "шаблон-final.pdf")
    return send_file("шаблон-final.pdf", as_attachment=True)

# Функция для проверки разрешенных расширений файлов
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}  # Допустимые расширения файлов
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)