from flask import Flask, request, jsonify, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Cấu hình SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# Thiết lập một khóa bí mật cho phiên
app.secret_key = 'ABCDEF'

# Khởi tạo SQLAlchemy và Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define models for Photo and User
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    photos = db.relationship('Photo', backref='user', lazy=True)

# Đăng nhập
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        session['user_id'] = user.id
        return jsonify(message='Login successful'), 200
    else:
        return jsonify(message='Invalid credentials'), 401

# Đăng ký
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='Registration successful'), 201

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Upload photo endpoint
@app.route('/api/photos', methods=['POST'])
def upload_photo():
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if 'user_id' not in session:
        print("User not logged in")  # Thêm log
        return jsonify(message='User not logged in'), 401

    user_id = session['user_id']

    if 'image' not in request.files:
        print("No image selected")  # Thêm log
        return jsonify(message='No image selected'), 400

    image = request.files['image']
    if image.filename == '':
        print("No image selected")  # Thêm log
        return jsonify(message='No image selected'), 400

    try:
        # Save the image to the server
        filename = secure_filename(f"{user_id}_{int(time.time())}.png")
        print(f"User ID: {user_id}, Filename: {filename}")  # Thêm log
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(save_path)

        # Kiểm tra xem tệp đã được lưu thành công không
        if not os.path.exists(save_path):
            raise Exception("Image not saved successfully")

        # Lưu thông tin ảnh vào danh sách ảnh của người dùng
        user = User.query.filter_by(id=user_id).first()
        if user:
            new_photo = Photo(user_id=user_id, url=f'/uploads/{filename}')
            db.session.add(new_photo)
            db.session.commit()

        # In ra danh sách ảnh hiện tại của người dùng sau khi cập nhật
        current_photos = [photo.url for photo in user.photos]
        print(f"Current images for User ID {user_id}: {current_photos}")  # Thêm log

        print("Photo saved successfully")  # Thêm log
        
        current_photos=[]
        return jsonify(message='Photo saved successfully'), 201
    except Exception as e:
        print(f"Error uploading photo: {str(e)}")
        return jsonify(message=f'Internal Server Error: {str(e)}'), 500

# Display photos endpoint
# Display photos endpoint
@app.route('/api/photos', methods=['GET'])
def display_photos():
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if 'user_id' not in session:
        return jsonify(message='User not logged in'), 401

    user_id = session['user_id']

    try:
        # Lấy danh sách ảnh của người dùng hiện tại
        photos = Photo.query.filter_by(user_id=user_id).all()
        current_photos = [photo.url for photo in photos]

        # In ra danh sách ảnh của người dùng hiện tại
        print(f"Current images for User ID {user_id}: {current_photos}")

        return jsonify([{'url': photo} for photo in current_photos])
    except Exception as e:
        return jsonify(message=str(e)), 500


if __name__ == '__main__':
    app.run(port=8080, use_reloader=False)
