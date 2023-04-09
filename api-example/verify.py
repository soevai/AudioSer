import requests
url = 'http://127.0.0.1:5620/code'
file = open('./1.png', 'rb')
files = {'file': ('1.png', file)}
response = requests.post(url, files=files)
print(response.json()['message'])
file.close()