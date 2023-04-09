import cv2
import mediapipe as mp
import threading
import requests
import pyaudio
import wave

# @Author > 忆梦
# @Date > 2023/4/3
# @Project > 手势语音识别

cap = cv2.VideoCapture(0)
sample_format = pyaudio.paInt16
chunk = 1024
channels = 1
fs = 44100
filename = "2.wav"

def sendcommit():
    url = 'http://127.0.0.1:5620/voice'
    file = open('./2.wav', 'rb')
    files = {'file': ('2.wav', file)}
    response = requests.post(url, files=files)
    return response.json()["message"]


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_tracking_confidence=0.01)
mp_drawing = mp.solutions.drawing_utils


p = pyaudio.PyAudio()
stream = p.open(
    format=sample_format,
    channels=channels,
    rate=fs, input=True,
    frames_per_buffer=chunk
)


def record_audio():
    print('please speak...')
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    frames = []
    while recording:
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    # print('录音结束.')
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    content = sendcommit()
    if content != "":
        print("you say：" + content)


def start_recording():
    global recording
    if not recording:
        recording = True
        t = threading.Thread(target=record_audio)
        t.start()


def stop_recording():
    global recording
    recording = False


recording = False


def main():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                joint_list = []
                for i, landmark in enumerate(hand_landmarks.landmark):
                    joint_list.append(
                        (int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])))

                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                x_thumb_tip, y_thumb_tip = int(
                    thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0])
                x_index_finger_tip, y_index_finger_tip = int(
                    index_finger_tip.x * frame.shape[1]), int(index_finger_tip.y * frame.shape[0])
                x_middle_finger_tip, y_middle_finger_tip = int(
                    middle_finger_tip.x * frame.shape[1]), int(middle_finger_tip.y * frame.shape[0])
                x_ring_finger_tip, y_ring_finger_tip = int(
                    ring_finger_tip.x * frame.shape[1]), int(ring_finger_tip.y * frame.shape[0])
                x_pinky_tip, y_pinky_tip = int(
                    pinky_tip.x * frame.shape[1]), int(pinky_tip.y * frame.shape[0])
                (x_thumb_tip + x_index_finger_tip +
                 x_middle_finger_tip + x_ring_finger_tip + x_pinky_tip) // 5
                palm_center_y = (y_thumb_tip + y_index_finger_tip +
                                 y_middle_finger_tip + y_ring_finger_tip + y_pinky_tip) // 5

                if palm_center_y > y_middle_finger_tip:
                    stop_recording()
                else:
                    start_recording()

        cv2.imshow("Hand Gestures", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nCaught Ctrl + C. Exiting")