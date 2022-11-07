import requests

URL = 'https://codex-api.herokuapp.com/'

data = {
  'code': "print('hello')",
  'language': 'py',
  'input': ''
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
  }

r = requests.post(url=URL, headers=headers, data=data)
j = r.json()
print(j)
print(j['output'])
