## AudioSer介绍

AudioSer是一个先进的深度学习语音识别API服务系统，它可以将上传的.wav格式的语音文件进行实时转换为文本，并返回给客户端支持多种语言和口音的语音识别，可以将语音实时转换为文本支持大规模并发请求通过缓存机制避免重复处理相同的文件。

### 技术细节
API使用了sherpa_ncnn库作为深度学习框架，使用了递归神经网络模型和长短时记忆网络模型对声学特征进行建模，进而对语音信号序列进行处理，从而实现语音信号的文字转换，再使用了Flask作为 Web 服务框架，通过RESTful API的方式与客户端交互。

### 目录结构
```python
AudioSer
├───model
│   ├───decoder_jit_trace-pnnx.ncnn.bin
│   ├───...
│   └───tokens.txt
│───cache
│   │───log
│   └───voice
│───sox
│   └───ffmpeg.exe
│───static
│   ├───css
│   ├───...
│   └───src
│───templates
│   └───index.html
└─── AudioSer.py
    |requirements.txt
    │README.md
    |config.py
    └───
```

<table style="width:100%">
  <tr>
    <th>AudioSer Web</th>
  </tr>
  <tr>
    <td><img src="/AudioSer/web.png" alt="AudioSer Web" height="400"></td>
  </tr>
</table>

### 如何使用
使用AudioSer，你需要向服务器发送HTTP请求，包含待转换的.wav格式的语音文件和相关参数。

安装第三方库：
```python
pip install -r requirements.txt
```

运行AudioSer:

```python
python AudioSer.py
```

Python调用示例：
```python
import requests

url = 'http://127.0.0.1:5620/voice'
file = open('E:/Desktop/1.wav', 'rb')
files = {'file': ('2.wav', file)}
response = requests.post(url, files=files).json()
print(response)
file.close()
```

```python
POST http://127.0.0.1:5620/voice 
Content-Type: audio/wav
```
在响应中，服务器将返回一段JSON格式的文本，其中包含了转换后的文本结果。

下面是一个示例响应：

```json
{ 
    "status": 200, 
    "message": "helloworld"
} 
```

```json
{ 
    "status": 200, 
    "message": "你好世界"
} 
```

### 结论 
AudioSer性能出色，可广泛应用于语音交互和自然语言处理等领域。
