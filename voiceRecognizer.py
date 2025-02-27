import os
import vosk
import json
import wave
import time
import numpy as np
from pydub import AudioSegment

# 初始化 Vosk 模型
model_path = r"E:\vosk-model-small-cn-0.22"  # 修改为你的模型路径
model = vosk.Model(model_path)
recognizer = vosk.KaldiRecognizer(model, 16000)

# 自动转换音频格式为 wav，并确保符合 Vosk 要求
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

# 分割音频文件
def split_audio(file_path, chunk_duration=300000):  # 5分钟
    audio = AudioSegment.from_file(file_path)
    chunks = []
    
    for i in range(0, len(audio), chunk_duration):
        chunk = audio[i:i + chunk_duration]
        chunk_path = f"chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    
    return chunks

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

# 显示进度和剩余时间
def process_audio_with_progress(file_path):
    # 将音频分成小段并处理
    chunks = split_audio(file_path)
    full_text = ""
    
    total_chunks = len(chunks)
    start_time = time.time()
    
    for idx, chunk in enumerate(chunks):
        print(f"正在处理第 {idx + 1}/{total_chunks} 段...")
        
        # 识别当前音频段
        text = recognize_audio(chunk)
        if text:
            full_text += text + "\n"
        
        # 显示进度和估算剩余时间
        elapsed_time = time.time() - start_time
        progress = (idx + 1) / total_chunks * 100
        estimated_time = (elapsed_time / (idx + 1)) * (total_chunks - (idx + 1))
        
        print(f"进度: {progress:.2f}% | 已用时间: {elapsed_time:.2f} 秒 | 估计剩余时间: {estimated_time:.2f} 秒")
    
    return full_text


def convert_to_vosk_wav(file_path):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1)  # 单声道
    audio = audio.set_sample_width(2)  # 16-bit
    audio = audio.set_frame_rate(16000)  # 16kHz 采样率
    wav_path = file_path.rsplit('.', 1)[0] + '_converted.wav'
    audio.export(wav_path, format='wav')
    return wav_path


# 主函数
def main():
    file_path = input("请输入音频文件路径：")

    if not os.path.exists(file_path):
        print("文件不存在！")
        return

    print("开始识别音频...")
    full_text = process_audio_with_progress(file_path)
    print("识别完成！识别结果：")
    print(full_text)

if __name__ == "__main__":
    main()
