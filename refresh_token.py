import requests

url = "https://accounts.zoho.eu/oauth/v2/token"

data = {
    "refresh_token": "-",
    "client_id": "-",
    "client_secret": "-",
    "grant_type": "refresh_token"
}

response = requests.post(url, data=data)
print(response.json())
