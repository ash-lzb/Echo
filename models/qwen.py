import os
import dashscope

messages = [
    {'role':'system','content':'you are a helpful assistant'},
    {'role': 'user','content': '你是谁？'}
]
responses = dashscope.Generation.call(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key="sk-d239f644a54d4c109e494a6e3f6b7697",
    model="qwen-plus", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=messages,
    result_format='message',
    stream=True,
    incremental_output=True
    )
for response in responses:
    print(response)  