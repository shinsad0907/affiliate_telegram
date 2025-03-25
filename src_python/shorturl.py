import requests

class SHORTEN:
    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'content-type': 'application/json',
            'origin': 'https://smartlink.mk',
            'priority': 'u=1, i',
            'referer': 'https://smartlink.mk/',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
    def bylink(self,link):
        json_data = {
            'link': link,
            'domain': '0fj.cc',
            'statusCode': '301',
            'deepLink': True,
        }

        response = requests.post('https://api.smartlink.mk/tools/shortener', headers=self.headers, json=json_data).json()
        return response['url']