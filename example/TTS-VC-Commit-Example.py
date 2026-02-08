import base64
import os
import threading
import dashscope
import pyaudio
from dashscope.audio.qwen_tts_realtime import *

qwen_tts_realtime: QwenTtsRealtime = None
text_to_synthesize = [
    '这是第一句话。',
    '这是第二句话。',
    '这是第三句话。',
]

player = pyaudio.PyAudio()
streamOutput = player.open(format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True)

DO_VIDEO_TEST = False

def init_dashscope_api_key():
    """
        Set your DashScope API-key. More information:
        https://github.com/aliyun/alibabacloud-bailian-speech-demo/blob/master/PREREQUISITES.md
    """

    # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    if 'DASHSCOPE_API_KEY' in os.environ:
        dashscope.api_key = os.environ[
            'DASHSCOPE_API_KEY']  # load API-key from environment variable DASHSCOPE_API_KEY
    else:
        dashscope.api_key = 'sk-d239f644a54d4c109e494a6e3f6b7697'  # set API-key manually



class MyCallback(QwenTtsRealtimeCallback):
    def __init__(self):
        super().__init__()
        self.response_counter = 0
        self.complete_event = threading.Event()
        self.file = open(f'result_{self.response_counter}_24k.pcm', 'wb')

    def reset_event(self):
        self.response_counter += 1
        self.file = open(f'result_{self.response_counter}_24k.pcm', 'wb')
        self.complete_event = threading.Event()

    def on_open(self) -> None:
        print('connection opened, init player')

    def on_close(self, close_status_code, close_msg) -> None:
        print('connection closed with code: {}, msg: {}, destroy player'.format(close_status_code, close_msg))

    def on_event(self, response: str) -> None:
        try:
            global qwen_tts_realtime
            type = response['type']
            if 'session.created' == type:
                print('start session: {}'.format(response['session']['id']))
            if 'response.audio.delta' == type:
                recv_audio_b64 = response['delta']
                sound_frame = base64.b64decode(recv_audio_b64)
                streamOutput.write(sound_frame)
                self.file.write(sound_frame)
            if 'response.done' == type:
                print(f'response {qwen_tts_realtime.get_last_response_id()} done')
                self.complete_event.set()
                self.file.close()
            if 'session.finished' == type:
                print('session finished')
                self.complete_event.set()
        except Exception as e:
            print('[Error] {}'.format(e))
            return

    def wait_for_response_done(self):
        self.complete_event.wait()


if __name__  == '__main__':
    init_dashscope_api_key()

    print('Initializing ...')

    callback = MyCallback()

    qwen_tts_realtime = QwenTtsRealtime(
        model='qwen3-tts-flash-realtime',
        callback=callback,
        # 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime
        url='wss://dashscope.aliyuncs.com/api-ws/v1/realtime'
        )

    qwen_tts_realtime.connect()
    qwen_tts_realtime.update_session(
        voice = 'Cherry',
        response_format = AudioFormat.PCM_24000HZ_MONO_16BIT,
        mode = 'commit'        
    )
    print(f'send texd: {text_to_synthesize[0]}')
    qwen_tts_realtime.append_text(text_to_synthesize[0])
    qwen_tts_realtime.commit()
    callback.wait_for_response_done()
    callback.reset_event()
    
    print(f'send texd: {text_to_synthesize[1]}')
    qwen_tts_realtime.append_text(text_to_synthesize[1])
    qwen_tts_realtime.commit()
    callback.wait_for_response_done()
    callback.reset_event()

    print(f'send texd: {text_to_synthesize[2]}')
    qwen_tts_realtime.append_text(text_to_synthesize[2])
    qwen_tts_realtime.commit()
    callback.wait_for_response_done()
    
    qwen_tts_realtime.finish()
    print('[Metric] session: {}, first audio delay: {}'.format(
                    qwen_tts_realtime.get_session_id(), 
                    qwen_tts_realtime.get_first_audio_delay(),
                    ))