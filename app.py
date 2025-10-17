# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import uuid
import os
from db_config import get_connection
from flask import send_from_directory
import pymysql
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.secret_key = '비밀키하나설정'  # 꼭 설정해야 세션이 작동함
app.config['UPLOAD_FOLDER'] = 'uploads'

# ✅ 로그인 라우트
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return "로그인 실패", 401
    return render_template('login.html')

# ✅ 로그아웃 라우트
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# ✅ 메인 페이지 보호
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('main.html')


@app.route('/residents')
def get_residents():
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as count FROM residents WHERE approved = 1")
    total_count = cursor.fetchone()['count']
    total_pages = (total_count + per_page - 1) // per_page

    cursor.execute(
        "SELECT id, name, unit_number AS address, phone, face_image_path AS photo_filename FROM residents WHERE approved = 1 ORDER BY id DESC LIMIT %s OFFSET %s",
        (per_page, offset)
    )
    residents = cursor.fetchall()

    conn.close()
    return jsonify({'data': residents, 'total_pages': total_pages})


@app.route('/admin/approve/<int:request_id>', methods=['POST'])
def approve_request(request_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM registration_requests WHERE id = %s", (request_id,))
        req = cursor.fetchone()
        if req:
            cursor.execute("""
                INSERT INTO residents (name, phone, unit_number, face_image_path)
                VALUES (%s, %s, %s, %s)
            """, (req['name'], req['phone'], req['unit_number'], req['face_image_path']))
            cursor.execute("UPDATE registration_requests SET status = 'approved' WHERE id = %s", (request_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_main'))

@app.route('/admin/reject/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE registration_requests SET status = 'rejected' WHERE id = %s", (request_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_main'))

@app.route('/register', methods=['POST'])
def register_request():
    name = request.form['name']
    phone = request.form['phone']
    unit_number = request.form['unit_number']
    file = request.files['face_image']

    # 이미지 저장
    filename = f"face_images/{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(app.static_folder, filename)
    file.save(file_path)

    # DB 저장
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO registration_requests (name, phone, unit_number, face_image_path)
            VALUES (%s, %s, %s, %s)
        """, (name, phone, unit_number, filename))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_main'))

import os
from flask import send_from_directory

@app.route('/qr')
def qr_page():
    qr_root = os.path.join(app.static_folder, 'qr')
    return send_from_directory(qr_root, 'index.html')

@app.route('/qr/<path:filename>')
def qr_assets(filename):
    qr_root = os.path.join(app.static_folder, 'qr')
    return send_from_directory(qr_root, filename)



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/verify_password', methods=['POST'])
def verify_password():
    data = request.get_json()
    if data.get('password') == '1234':
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'fail'})


@app.route('/logs')
def get_logs():
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 10))
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM qr_logs ORDER BY timestamp DESC LIMIT %s OFFSET %s
        """, (limit, skip))
        logs = cursor.fetchall()
    return jsonify(logs)

@app.route('/entry_logs')
def entry_logs():
    resident_type = request.args.get('type', '세대주')
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.datetime, r.address, e.purpose, r.name, r.phone
            FROM entry_logs e
            JOIN residents r ON e.resident_id = r.id
            WHERE e.resident_type = %s
            ORDER BY e.datetime DESC
        """, (resident_type,))
        records = cursor.fetchall()
    return jsonify(records)

@app.route('/residents/<int:resident_id>', methods=['PUT'])
def update_resident(resident_id):
    name = request.form['name']
    address = request.form['address']
    phone = request.form['phone']
    file = request.files.get('photo')

    conn = get_connection()
    with conn.cursor() as cursor:
        if file:
            filename = f"face_images/{uuid.uuid4().hex}.jpg"
            file.save(os.path.join(app.static_folder, filename))
            cursor.execute("""
                UPDATE residents SET name=%s, unit_number=%s, phone=%s, face_image_path=%s WHERE id=%s
            """, (name, address, phone, filename, resident_id))
        else:
            cursor.execute("""
                UPDATE residents SET name=%s, unit_number=%s, phone=%s WHERE id=%s
            """, (name, address, phone, resident_id))
    conn.commit()
    conn.close()
    return '', 204

from flask import request, jsonify


@app.route('/residents/<int:resident_id>', methods=['DELETE'])
def delete_resident(resident_id):
    data = request.get_json()
    if not verify_password(data.get('password')):
        return {'status': 'error'}, 403

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM residents WHERE id = %s", (resident_id,))
    conn.commit()
    conn.close()
    return '', 204




# ✅ 맨 마지막에 실행
if __name__ == '__main__':
    app.run(debug=True)