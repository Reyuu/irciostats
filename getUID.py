import json
import requests

token = ""
with open("token.txt", "r") as f:
    token = f.read()
base = "https://osu.ppy.sh/api/"

headers = {"Content-Type": "application/json", "Authorization": "Bearer {0}".format(token)}

def get_user_id(nick):
    api_url = "{0}get_user".format(base)
    payload = {"k": token, "u": "{0}".format(nick), "type": "string"}
    response = requests.get(api_url, headers=headers, params=payload)
    try:
        return response.json()[0]["user_id"]
    except KeyError:
        return -1
    except IndexError:
        return -1