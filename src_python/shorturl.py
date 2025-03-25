import requests

class SHORTEN:
    def __init__(self):
        self.cookies = {
            '_ga': 'GA1.1.1288068479.1742667378',
            'PHPSESSID': 'hvok4lhc5ks0u2io74icna0285',
            '_ga_W7VH9N2DP3': 'GS1.1.1742921386.3.0.1742921386.0.0.0',
        }

        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryxgztGpFSJNFRqvPN',
            'origin': 'https://by.com.vn',
            'priority': 'u=1, i',
            'referer': 'https://by.com.vn/',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/',
            'x-requested-with': 'XMLHttpRequest',
        }
    def bylink(self,link):
        files = {
            'url': (None, link),
        }

        response = requests.post('https://by.com.vn/shorten', cookies=self.cookies, headers=self.headers, files=files)
        return response.json()['shorturl']