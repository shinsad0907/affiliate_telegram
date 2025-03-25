# import requests
# from supabase import create_client
# SQL_url = "https://fcexovcykhpgdjbffzpk.supabase.co"
# SQL_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZjZXhvdmN5a2hwZ2RqYmZmenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5MTUxMjYsImV4cCI6MjA1ODQ5MTEyNn0.22C54odvwLCCZrSkTX_k22SvZ0e6Q4a9TLvGRUb-FoE"
# supabase = create_client(SQL_url, SQL_key)
# device_control_response = supabase.table("link").select("*").execute()
# for device in device_control_response.data:
#     print(device['link'])
#         # save_requests_SQL = supabase.table("new_devices").insert({
#         #     "link": device['link'],
#         # }).execute()
# # save_requests_SQL = supabase.table("new_devices").insert({
# #     "link": "https://www.google.com",
# # }).execute()


import requests
from supabase import create_client

class GET_DATA:
    def __init__(self):
        self.url = 'https://fcexovcykhpgdjbffzpk.supabase.co'
        self.key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZjZXhvdmN5a2hwZ2RqYmZmenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5MTUxMjYsImV4cCI6MjA1ODQ5MTEyNn0.22C54odvwLCCZrSkTX_k22SvZ0e6Q4a9TLvGRUb-FoE'
        self.supabase = create_client(self.url, self.key)

    def get_data_link(self):
        data_link = {}
        device_control_response = self.supabase.table("link").select("*").execute()
        return device_control_response.data
