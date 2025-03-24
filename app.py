from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from functools import wraps
import requests
import os
import json
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Telegram Bot Config
BOT_TOKEN = '8007401555:AAFM76K8fJnfSyL83O3cXEIFzAaAQE7pHrw'
CHAT_ID = '-1002666277835'

# Database setup
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Bạn phải đăng nhập để truy cập chức năng này.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    db = get_db()
    channels = db.execute('SELECT * FROM channels').fetchall()
    return render_template('index.html', channels=channels)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Simple authentication logic (replace with your own logic)
    if username == 'admin' and password == 'password':
        session['logged_in'] = True
        session['username'] = username
        flash('Đăng nhập thành công!', 'success')
    else:
        flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Đăng xuất thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/add_channel', methods=['POST'])
@login_required
def add_channel():
    name = request.form.get('name')
    chat_id = request.form.get('chat_id')
    
    db = get_db()
    existing_channel = db.execute('SELECT * FROM channels WHERE id = ?', (chat_id,)).fetchone()
    if existing_channel:
        flash('Channel này đã tồn tại!', 'warning')
        return redirect(url_for('index'))
    
    db.execute('INSERT INTO channels (id, name, date_added) VALUES (?, ?, ?)',
               (chat_id, name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    db.commit()
    flash('Đã thêm channel thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/channel/<channel_id>')
@login_required
def channel_detail(channel_id):
    db = get_db()
    channel = db.execute('SELECT * FROM channels WHERE id = ?', (channel_id,)).fetchone()
    if not channel:
        flash('Không tìm thấy channel!', 'danger')
        return redirect(url_for('index'))
    posts = db.execute('SELECT * FROM posts WHERE channel_id = ?', (channel_id,)).fetchall()
    return render_template('channel_detail.html', channel=channel, posts=posts)

@app.route('/channel/<channel_id>/post/<int:post_id>')
@login_required
def post_detail(channel_id, post_id):
    db = get_db()
    channel = db.execute('SELECT * FROM channels WHERE id = ?', (channel_id,)).fetchone()
    if not channel:
        flash('Không tìm thấy channel!', 'danger')
        return redirect(url_for('index'))
    
    post = db.execute('SELECT * FROM posts WHERE id = ? AND channel_id = ?', (post_id, channel_id)).fetchone()
    if not post:
        flash('Không tìm thấy bài đăng!', 'danger')
        return redirect(url_for('channel_detail', channel_id=channel_id))
    
    return render_template('post_detail.html', channel=channel, post=post)

@app.route('/upload/<channel_id>', methods=['POST'])
@login_required
def upload(channel_id):
    db = get_db()
    channel = db.execute('SELECT * FROM channels WHERE id = ?', (channel_id,)).fetchone()
    if not channel:
        flash('Không tìm thấy channel!', 'danger')
        return redirect(url_for('index'))
    
    media_files = request.files.getlist('media')
    caption = request.form.get('caption', '')
    media_group = []

    # Không có file được chọn
    if not media_files or media_files[0].filename == '':
        flash('Vui lòng chọn file!', 'warning')
        return redirect(url_for('channel_detail', channel_id=channel_id))

    media_file_info = []
    for media in media_files:
        if media:
            media_path = os.path.join(app.config['UPLOAD_FOLDER'], media.filename)
            media.save(media_path)
            
            # Xác định loại media
            media_type = 'photo' if media.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')) else 'video'
            media_group.append({
                'type': media_type,
                'media': f'attach://{media.filename}'
            })
            media_file_info.append({
                'type': media_type,
                'filename': media.filename
            })

    files = {media.filename: open(os.path.join(app.config['UPLOAD_FOLDER'], media.filename), 'rb') for media in media_files}
    
    # Thêm caption vào media đầu tiên
    if caption and media_group:
        media_group[0]['caption'] = caption

    response = requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup',
        data={'chat_id': channel_id, 'media': str(media_group).replace("'", '"')},
        files=files
    )

    # Đóng tất cả các file đã mở
    for f in files.values():
        f.close()

    if response.status_code == 200:
        # Lưu thông tin bài đăng vào dữ liệu channel
        db.execute('INSERT INTO posts (channel_id, caption, media_count, date, media_files) VALUES (?, ?, ?, ?, ?)',
                   (channel_id, caption, len(media_file_info), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(media_file_info)))
        db.commit()
        flash('Đã đăng bài thành công!', 'success')
    else:
        flash(f'Lỗi khi gửi tới Telegram: {response.text}', 'danger')

    return redirect(url_for('channel_detail', channel_id=channel_id))

@app.route('/delete_channel/<channel_id>', methods=['POST'])
@login_required
def delete_channel(channel_id):
    db = get_db()
    db.execute('DELETE FROM channels WHERE id = ?', (channel_id,))
    db.execute('DELETE FROM posts WHERE channel_id = ?', (channel_id,))
    db.commit()
    flash('Đã xóa channel thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_post/<channel_id>/<int:post_id>', methods=['POST'])
@login_required
def delete_post(channel_id, post_id):
    db = get_db()
    db.execute('DELETE FROM posts WHERE id = ? AND channel_id = ?', (post_id, channel_id))
    db.commit()
    flash('Đã xóa bài đăng thành công!', 'success')
    return redirect(url_for('channel_detail', channel_id=channel_id))

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
