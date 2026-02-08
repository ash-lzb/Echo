import pyaudio
import numpy as np

def play_pcm_with_pyaudio(file_path, sample_rate=44100, channels=1, 
                         sample_width=2, subtype='PCM_16'):
    """
    播放PCM文件
    
    参数：
    - file_path: PCM文件路径
    - sample_rate: 采样率（Hz），常见值：8000, 16000, 44100, 48000
    - channels: 声道数，1=单声道，2=立体声
    - sample_width: 样本宽度（字节），2=16位，3=24位
    - subtype: 数据类型，'PCM_16'=16位整数
    """
    
    # PCM样本宽度到PyAudio格式的映射
    format_map = {
        1: pyaudio.paInt8,      # 8位
        2: pyaudio.paInt16,     # 16位
        3: pyaudio.paInt24,     # 24位
        4: pyaudio.paInt32      # 32位
    }
    
    p = pyaudio.PyAudio()
    
    # 打开音频流
    stream = p.open(
        format=format_map.get(sample_width, pyaudio.paInt16),
        channels=channels,
        rate=sample_rate,
        output=True
    )
    
    # 读取并播放PCM数据
    chunk_size = 1024  # 每次读取的帧数
    
    with open(file_path, 'rb') as f:
        data = f.read(chunk_size * channels * sample_width)
        while data:
            stream.write(data)
            data = f.read(chunk_size * channels * sample_width)
    
    # 清理资源
    stream.stop_stream()
    stream.close()
    p.terminate()


def player(frames):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=24000,
                    output=True)
    
    stream.write(frames)