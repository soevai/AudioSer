import time
import requests

url = 'http://127.0.0.1:5620/voice'
file = open('./1.wav', 'rb')
files = {'file': ('1.wav', file)}

start_time = time.perf_counter()

response = requests.post(url, files=files)

end_time = time.perf_counter()

file.close()

print(response.json())
print("Code execution time:", end_time - start_time, "seconds")
