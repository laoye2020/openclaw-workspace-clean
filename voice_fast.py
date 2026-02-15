#!/usr/bin/env python3
"""
🎙️ 快速语音回复 - 使用常驻 Whisper 服务
"""

import sys
import requests
import tempfile

def transcribe(audio_path: str) -> str:
    """调用常驻 Whisper 服务"""
    try:
        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            response = requests.post('http://127.0.0.1:8007/transcribe', files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('text', '') if result.get('success') else None
        return None
    except Exception as e:
        print(f"识别失败: {e}", file=sys.stderr)
        return None

def text_to_speech(text: str, output_path: str):
    """调用 CosyVoice 服务生成语音"""
    try:
        params = {
            'text': text,
            'speed': 0.94,
            'temperature': 0.78,
            'top_p': 0.82,
            'top_k': 32,
            'style': 'seraphine',
            'style_strength': 1.18
        }
        response = requests.get('http://localhost:8006/speak', params=params, timeout=60)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        print(f"语音生成失败: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 voice_fast.py <输入音频> <输出音频> [回复文字]")
        sys.exit(1)
    
    input_audio = sys.argv[1]
    output_audio = sys.argv[2]
    reply_text = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 1. 识别语音
    print(f"🎙️ 识别中...", file=sys.stderr)
    text = transcribe(input_audio)
    if not text:
        print("❌ 识别失败", file=sys.stderr)
        sys.exit(1)
    
    print(f"识别结果: {text}")
    
    # 2. 生成回复语音
    if reply_text:
        print(f"🎙️ 生成语音: {reply_text[:30]}...", file=sys.stderr)
        if text_to_speech(reply_text, output_audio):
            print(f"✅ 已保存: {output_audio}", file=sys.stderr)
        else:
            print("❌ 语音生成失败", file=sys.stderr)
            sys.exit(1)
