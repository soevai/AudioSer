import pyaudio
import wave
import numpy as np
import requests
import time
import threading
import matplotlib.pyplot as plt

# @Author > 忆梦
# @Date > 2023/4/3
# @Project > 声音检测识别

CHUNK, CHANNELS, RATE = 1024, 1, 44100
FORMAT = pyaudio.paInt16
THRESHOLD = 500
PREV_RECORD_TIME = 0.1

p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

def sendcommit():
    url = 'http://127.0.0.1:5620/voice'
    file = open('./2.wav', 'rb')
    files = {'file': ('2.wav', file)}
    response = requests.post(url, files=files)
    return response.json()["message"]

def callKernel():
    try:
        print('Please speak ...')
        record_audio('2.wav', 2 - PREV_RECORD_TIME) 
        time.sleep(PREV_RECORD_TIME)
        content = sendcommit()
        if content != "":
            print("you say：" + content)
    except Exception:
        pass


def record_audio(wave_out_path, record_second):
    wf = wave.open(wave_out_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size((FORMAT)))
    wf.setframerate(RATE)
    for _ in range(0, int(RATE * record_second / CHUNK)):
        data = stream.read(CHUNK)
        wf.writeframes(data)
    wf.close()

def plot_waveform():
    np.zeros(CHUNK, dtype=np.short)
    plt.ion()
    fig, ax = plt.subplots()
    x = np.arange(0, CHUNK)
    line, = ax.plot(x, np.zeros(CHUNK))

    while True:
        string_audio_data = stream.read(CHUNK)
        audio_data = np.frombuffer(string_audio_data, dtype=np.short)
        line.set_ydata(audio_data)
        ax.relim()
        ax.autoscale_view(True,True,True)
        fig.canvas.draw()
        fig.canvas.flush_events()


if __name__ == "__main__":
    try:
        waveform_thread = threading.Thread(target=plot_waveform)
        waveform_thread.start()
        while True:
            string_audio_data = stream.read(CHUNK)
            audio_data = np.frombuffer(string_audio_data, dtype=np.short)
            if sum(abs(audio_data)) // CHUNK >= THRESHOLD:
                callKernel()

    except KeyboardInterrupt:
        print("\nCaught Ctrl + C. Exiting")