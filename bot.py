# # import requests 
# import requests

# # Thông tin bot và kênh
# BOT_TOKEN = '8007401555:AAFM76K8fJnfSyL83O3cXEIFzAaAQE7pHrw'
# CHAT_ID = '-1002666277835'  # Ví dụ: '-1001234567890'
# API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

# # Nội dung tin nhắn
# message = "Hello, world!"

# # Gửi tin nhắn
# response = requests.post(API_URL, data={'chat_id': CHAT_ID, 'text': message})

# # Kiểm tra kết quả
# if response.status_code == 200:
#     print("Gửi tin nhắn thành công!")
# else:
#     print("Lỗi:", response.text)

import requests

# Thông tin bot và kênh
BOT_TOKEN = '8007401555:AAFM76K8fJnfSyL83O3cXEIFzAaAQE7pHrw'
CHAT_ID = '-1002666277835'  # ID của kênh
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendVideo'

# Đường dẫn video (local hoặc URL trực tiếp)
video_path = r'C:\shin\shinsad\tool_affiliate\tool_telegram\video.mp4'
caption = "Đây là video từ bot!"

# Mở file video và gửi
with open(video_path, 'rb') as video_file:
    response = requests.post(API_URL, data={'chat_id': CHAT_ID, 'caption': caption}, files={'video': video_file})

# Kiểm tra kết quả
if response.status_code == 200:
    print("Gửi video thành công!")
else:
    print("Lỗi:", response.text)
    