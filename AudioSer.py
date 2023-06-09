import logging, ddddocr
import sherpa_ncnn, wave
import uuid, shlex, os
import subprocess, mimetypes
import numpy as np
from flask_caching import Cache
from flask import (
    Flask, request, jsonify,
    render_template
)

# @Author > 忆梦
# @Date > 2023/4/3
# @Project > 语音识别API服务

HOST = ['127.0.0.1', '5620']
VO_UPLOAD_FOLDER = './cache/voice/'
IM_UPLOAD_FOLDER = './cache/image/'
ALLOWED_EXTENSIONS = ['wav', 'png']
ALLOWED_MIME_TYPES = ['audio/wav', 'audio/x-wav', 'image/png']

ENCODER_PARMA = './model/encoder_jit_trace-pnnx.ncnn.param'
ENCODER_BIN = './model/encoder_jit_trace-pnnx.ncnn.bin'
DECODER_PARAM = './model/decoder_jit_trace-pnnx.ncnn.param'
DECODER_BIN = './model/decoder_jit_trace-pnnx.ncnn.bin'
JOINER_PARAM = './model/joiner_jit_trace-pnnx.ncnn.param'
JOINER_BIN = './model/joiner_jit_trace-pnnx.ncnn.bin'
TOKENS = './model/tokens.txt'
NUM_THREADS = 4

SINGLE_PLAYER_MODE = False

Server = Flask(__name__)

Server.config['IM_UPLOAD_FOLDER'] = IM_UPLOAD_FOLDER
Server.config['VO_UPLOAD_FOLDER'] = VO_UPLOAD_FOLDER
Server.config['CACHE_TYPE'] = 'simple'
Server.config['CACHE_DEFAULT_TIMEOUT'] = 1
cache = Cache(Server)
ocr = ddddocr.DdddOcr()

recognizer = sherpa_ncnn.Recognizer(
    tokens=TOKENS, encoder_param=ENCODER_PARMA,
    encoder_bin=ENCODER_BIN, decoder_param=DECODER_PARAM,
    decoder_bin=DECODER_BIN, joiner_param=JOINER_PARAM,
    joiner_bin=JOINER_BIN, num_threads=NUM_THREADS
)


def rewrite(input_file, output_file):
    command = ["./sox/ffmpeg", "-i", shlex.quote(input_file),
               "-ac", "1","-ar", "16000", shlex.quote(output_file), "-y"]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@cache.memoize()
def Voice_recognition(filename):
    with wave.open(filename, 'rb') as f:
        if f.getframerate() != recognizer.sample_rate:
            raise ValueError(
                f"Invalid sample rate: {f.getframerate()}, expected {recognizer.sample_rate}. File: {filename}")
        if f.getnchannels() != 1:
            raise ValueError(
                f"Invalid number of channels: {f.getnchannels()}, expected 1. File: {filename}")
        if f.getsampwidth() != 2:
            raise ValueError(
                f"Invalid sample width: {f.getsampwidth()}, expected 2. File: {filename}")

        num_samples = f.getnframes()
        samples = f.readframes(num_samples)
        samples_int16 = np.frombuffer(samples, dtype=np.int16)
        samples_float32 = samples_int16.astype(np.float32)
        samples_float32 /= 32768

    recognizer.accept_waveform(recognizer.sample_rate, samples_float32)
    tail_paddings = np.zeros(
    int(recognizer.sample_rate * 0.5), dtype=np.float32)
    recognizer.accept_waveform(recognizer.sample_rate, tail_paddings)
    res1 = recognizer.text.lower()
    recognizer.reset()
    return res1


def configure_app():
    if not os.path.exists(VO_UPLOAD_FOLDER):
        os.makedirs(VO_UPLOAD_FOLDER)
    cache.init_app(Server)


def configure_log():
    logging.basicConfig(level=logging.INFO, filename='./cache/log/server.log',
    format='%(levelname)s:%(asctime)s %(message)s')


def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type is None or mime_type not in ALLOWED_MIME_TYPES:
        return False
    return True

def delete_file(filepath, output_filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

    if os.path.exists(output_filepath):
        os.remove(output_filepath)

def check_type(mode, nfile):
    if 'file' not in request.files:
        raise ValueError('No file part.')

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        raise ValueError('Please upload a .wav file.')

    if SINGLE_PLAYER_MODE:
        filename = "source" + nfile
    else:
        filename = str(uuid.uuid4()) + nfile

    filepath = os.path.join(Server.config[mode], filename)
    file.save(filepath)
    output_filepath = os.path.join(Server.config[mode], 'output_' + filename)
    return filepath, output_filepath


@Server.route('/code', methods=['POST'])
def Verifcode():
    try:
        if request.method == 'POST':
            filepath, output_filepath = check_type('IM_UPLOAD_FOLDER', '.png')
            with open(filepath, 'rb') as f:
                img_bytes = f.read()
            res = ocr.classification(img_bytes)
            delete_file(filepath, output_filepath)
            return jsonify({
                'status': 200,
                'message': res
            })
    except Exception as e:
        logging.error(f"Recognition error: {e}")
        delete_file(filepath, output_filepath)
        return jsonify({
            'status': 500,
            'message': 'Error, Please try again later.'
        })
    
@Server.route('/voice', methods=['POST'])
def upload_file():
    try:
        if request.method == 'POST':
            filepath, output_filepath = check_type('VO_UPLOAD_FOLDER', '.wav')
            rewrite(filepath, output_filepath)

            result = Voice_recognition(output_filepath)
            delete_file(filepath, output_filepath)

            return jsonify({
                'status': 200,
                'message': result
            })

    except ValueError as e:
        return jsonify({
            'status': 400,
            'message': "Audio signals don't exist"
        })

    except Exception as e:
        delete_file(filepath, output_filepath)
        logging.error(f"Recognition error: {e}")
        return jsonify({
            'status': 500,
            'message': 'Error, Please try again later.'
        })


@Server.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    configure_app()
    configure_log()
    print(f" * Running on http://{HOST[0]}:{HOST[1]}")
    os.system(f"start http://{HOST[0]}:{HOST[1]}")
    Server.run(host=HOST[0], port=HOST[1], debug=False)