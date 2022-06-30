import requests
import json
url = 'https://api.github.com'
user ='FedorLog'
r = requests.get(f'{url}/users/{user}/repos')
with open('data.json', 'w') as file:
    json.dump(r.json(), f)
for i in r.json():
    print(i['name'])
