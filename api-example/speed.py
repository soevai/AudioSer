import requests
import time

def sendGet():
    url = 'http://127.0.0.1:5620/voice'
    file = open('E:/Desktop/1.wav', 'rb')
    files = {'file': ('1.wav', file)}
    response = requests.post(url, files=files).json()
    print(response)
    file.close()

def loop():
    for _ in range(10):
        sendGet()

start_time = time.time()
loop()
#sendGet()
end_time = time.time()
total_time = end_time - start_time
print(f"Total time: {total_time} seconds")