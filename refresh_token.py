import requests
import os
from dotenv import load_dotenv

load_dotenv()

refresh_token = os.getenv('REFRESH_TOKEN')
cliend_id= os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

url = "https://accounts.zoho.eu/oauth/v2/token"

data = {
    "refresh_token": "-",
    "client_id": "-",
    "client_secret": "-",
    "grant_type": "refresh_token"
}

response = requests.post(url, data=data)
print(response.json())
