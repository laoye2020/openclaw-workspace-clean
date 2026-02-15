#!/usr/bin/env python3
"""
🎙️ Whisper 客户端 - 调用常驻服务
"""

import sys
import requests

def transcribe(audio_path: str) -> str:
    """调用 Whisper 服务进行语音识别"""
    try:
        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            response = requests.post('http://127.0.0.1:8007/transcribe', files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('text', '')
            else:
                print(f"识别失败: {result.get('error')}")
                return None
        else:
            print(f"请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"异常: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 whisper_client.py <音频文件路径>")
        sys.exit(1)
    
    text = transcribe(sys.argv[1])
    if text:
        print(text)
    else:
        sys.exit(1)
