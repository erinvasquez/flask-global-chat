import os

fullchain_path = '/etc/letsencrypt/live/silenttableshow.com/fullchain.pem'
privkey_path = '/etc/letsencrypt/live/silenttableshow.com/privkey.pem'

try:
    with open(fullchain_path, 'r') as f:
        print("Read fullchain.pem successfully")
    with open(privkey_path, 'r') as f:
        print("Read privkey.pem successfully")
except Exception as e:
    print(f"Error: {e}")
