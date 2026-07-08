import os
import base64
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# [핵심 변경] 브라우저 쿠키 대신, 서버 내 전역 변수(메모리)에 사진 데이터를 누적 저장합니다.
# 브라우저 용량 제한(4KB)의 영향을 전혀 받지 않으므로 수백 장을 올려도 끄떡없습니다.
GLOBAL_SECTION_PHOTOS = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    global GLOBAL_SECTION_PHOTOS

    if request.method == 'POST':
        if 'photos' not in request.files:
            return redirect(request.url)
        
        files = request.files.getlist('photos')
        section_name = request.form.get('section_name', '기본 구역').strip()
        
        # 해당 구역이 메모리에 없으면 새 리스트 생성
        if section_name not in GLOBAL_SECTION_PHOTOS:
            GLOBAL_SECTION_PHOTOS[section_name] = []

        for file in files:
            if file.filename == '':
                continue
            
            if file:
                photo_name = os.path.splitext(file.filename)[0]
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                
                # 이미지 용량을 고려하여 Base64로 안전하게 변환
                with open(filepath, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
                    if ext == 'jpg': ext = 'jpeg'
                    b64_url = f"data:image/{ext};base64,{encoded_string}"

                # 기존 구역 데이터 뒤에 차곡차곡 누적 추가
                GLOBAL_SECTION_PHOTOS[section_name].append({
                    'url': b64_url,
                    'name': photo_name
                })
        
        return redirect(url_for('index'))
    
    return render_template('index.html', section_photos=GLOBAL_SECTION_PHOTOS)

# 전체 데이터를 싹 비우는 초기화 라우트
@app.route('/clear', methods=['POST'])
def clear_all():
    global GLOBAL_SECTION_PHOTOS
    GLOBAL_SECTION_PHOTOS.clear() # 서버 메모리 완전 비우기
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
