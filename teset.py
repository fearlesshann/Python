
import os
import vosk
import json
import wave
from pydub import AudioSegment
import numpy as np

# 初始化 Vosk 模型
model_path = r"E:\vosk-model-small-cn-0.22"  # 修改为你的模型路径
model = vosk.Model(model_path)
recognizer = vosk.KaldiRecognizer(model, 16000)

# 自动转换音频格式为wav，并确保符合 Vosk 要求
def convert_to_wav(file_path):
    # 获取文件扩展名
    file_extension = file_path.split('.')[-1].lower()

    # 如果是需要转换的格式（例如 m4a、mp3、flac 等），则使用 pydub 转换为 wav
    if file_extension in ['m4a', 'mp3', 'flac', 'ogg', 'aac']:
        print(f"正在将 {file_path} 转换为 .wav 格式...")
        audio = AudioSegment.from_file(file_path, format=file_extension)
        
        # 确保音频是单声道、16 位、16000 Hz 采样率
        audio = audio.set_channels(1)  # 单声道
        audio = audio.set_sample_width(2)  # 16 位
        audio = audio.set_frame_rate(16000)  # 16000 Hz 采样率

        # 保存转换后的文件
        wav_path = file_path.rsplit('.', 1)[0] + '.wav'
        audio.export(wav_path, format='wav')
        print(f"转换完成，保存为: {wav_path}")
        return wav_path
    elif file_extension == 'wav':
        print("文件格式是 .wav，无需转换。")
        return file_path
    else:
        raise ValueError(f"不支持的音频格式：{file_extension}")

# 读取音频文件并进行识别
def recognize_audio(file_path):
    # 将音频转换为 wav 格式（如果不是 wav 格式）
    try:
        file_path = convert_to_wav(file_path)
    except ValueError as ve:
        print(ve)
        return None

    # 打开转换后的 wav 文件
    with wave.open(file_path, 'rb') as wf:
        frames = wf.getnframes()
        buffer = wf.readframes(frames)
        audio_data = np.frombuffer(buffer, dtype=np.int16)

        # 将 numpy.ndarray 转换为字节类型
        audio_bytes = audio_data.tobytes()

        # 进行语音识别
        if recognizer.AcceptWaveform(audio_bytes):  # 使用字节数据
            result = recognizer.Result()
            print("识别成功:", result)
            text = json.loads(result).get('text', '')
            return text
        else:
            print("无法识别音频内容。")
            return None

# 主函数
def main():
    file_path = input("请输入音频文件路径：")

    if not os.path.exists(file_path):
        print("文件不存在！")
        return

    print("开始识别音频...")
    text = recognize_audio(file_path)
    if text:
        print("识别结果：", text)

if __name__ == "__main__":
    main()
