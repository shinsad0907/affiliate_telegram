from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from functools import wraps
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Sử dụng thư mục tạm (thường áp dụng cho môi trường serverless như AWS Lambda)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Telegram Bot Config
BOT_TOKEN = '8007401555:AAFM76K8fJnfSyL83O3cXEIFzAaAQE7pHrw'
CHAT_ID = '-1002666277835'

# Đường dẫn file lưu trữ dữ liệu kênh
CHANNELS_FILE = '/tmp/channels.json'


# Hàm đọc dữ liệu channels từ file JSON
def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Hàm lưu dữ liệu channels vào file JSON
def save_channels(channels):
    with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(channels, f, ensure_ascii=False, indent=4)

# Hàm tìm channel theo ID
def find_channel(channel_id):
    channels = load_channels()
    for channel in channels:
        if channel['id'] == channel_id:
            return channel
    return None

# Hàm thêm bài đăng mới vào channel
def add_post_to_channel(channel_id, media_files, caption):
    channels = load_channels()
    for channel in channels:
        if channel['id'] == channel_id:
            post_id = len(channel.get('posts', [])) + 1
            post = {
                'id': post_id,
                'caption': caption,
                'media_count': len(media_files),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'media_files': media_files
            }
            if 'posts' not in channel:
                channel['posts'] = []
            channel['posts'].append(post)
            channel['post_count'] = len(channel['posts'])
            save_channels(channels)
            return True
    return False
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
    channels = load_channels()
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
    
    channels = load_channels()
    # Kiểm tra xem channel đã tồn tại chưa
    for channel in channels:
        if channel['id'] == chat_id:
            flash('Channel này đã tồn tại!', 'warning')
            return redirect(url_for('index'))
    
    new_channel = {
        'id': chat_id,
        'name': name,
        'posts': [],
        'post_count': 0,
        'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    channels.append(new_channel)
    save_channels(channels)
    flash('Đã thêm channel thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/channel/<channel_id>')
@login_required
def channel_detail(channel_id):
    channel = find_channel(channel_id)
    if not channel:
        flash('Không tìm thấy channel!', 'danger')
        return redirect(url_for('index'))
    return render_template('channel_detail.html', channel=channel, posts=channel.get('posts', []))
@app.route('/channel/<channel_id>/post/<int:post_id>')
@login_required
def post_detail(channel_id, post_id):
    channel = find_channel(channel_id)
    if not channel:
        flash('Không tìm thấy channel!', 'danger')
        return redirect(url_for('index'))
    
    post = next((p for p in channel.get('posts', []) if p['id'] == post_id), None)
    if not post:
        flash('Không tìm thấy bài đăng!', 'danger')
        return redirect(url_for('channel_detail', channel_id=channel_id))
    
    return render_template('post_detail.html', channel=channel, post=post)
@app.route('/upload/<channel_id>', methods=['POST'])
@login_required
def upload(channel_id):
    channel = find_channel(channel_id)
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
        add_post_to_channel(channel_id, media_file_info, caption)
        flash('Đã đăng bài thành công!', 'success')
    else:
        flash(f'Lỗi khi gửi tới Telegram: {response.text}', 'danger')

    return redirect(url_for('channel_detail', channel_id=channel_id))

@app.route('/delete_channel/<channel_id>', methods=['POST'])
@login_required
def delete_channel(channel_id):
    channels = load_channels()
    channels = [c for c in channels if c['id'] != channel_id]
    save_channels(channels)
    flash('Đã xóa channel thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_post/<channel_id>/<int:post_id>', methods=['POST'])
@login_required
def delete_post(channel_id, post_id):
    channels = load_channels()
    for channel in channels:
        if channel['id'] == channel_id:
            channel['posts'] = [p for p in channel['posts'] if p['id'] != post_id]
            channel['post_count'] = len(channel['posts'])
            save_channels(channels)
            flash('Đã xóa bài đăng thành công!', 'success')
            break
    return redirect(url_for('channel_detail', channel_id=channel_id))

if __name__ == '__main__':
    # Tạo file channels.json nếu chưa tồn tại
    if not os.path.exists(CHANNELS_FILE):
        save_channels([{
            'id': CHAT_ID,
            'name': 'Channel mặc định',
            'posts': [],
            'post_count': 0,
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
    app.run(debug=True)