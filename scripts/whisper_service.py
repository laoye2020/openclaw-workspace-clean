#!/usr/bin/env python3
"""
Whisper 语音转文字服务
用于 Telegram 语音消息处理
"""

import sys
import os
import whisper
import tempfile

def transcribe_audio(audio_path, language='zh'):
    """将音频转为文字"""
    # 加载模型（第一次会自动下载）
    model = whisper.load_model("base")
    
    # 转录
    result = model.transcribe(audio_path, language=language)
    
    return result["text"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 whisper_service.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    if not os.path.exists(audio_file):
        print(f"Error: File not found: {audio_file}")
        sys.exit(1)
    
    try:
        text = transcribe_audio(audio_file)
        print(text)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
