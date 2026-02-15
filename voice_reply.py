#!/usr/bin/env python3
"""
🎙️ OpenClaw 语音助手 - 处理语音消息
在 OpenClaw 会话中调用，不占用 Bot 连接
"""

import os
import sys
import io
import tempfile
import requests
from pathlib import Path

# 配置
VOICE_SERVICE_URL = 'http://localhost:8006/speak'
VOICE_PARAMS = {
    'speed': 0.94,
    'temperature': 0.78,
    'top_p': 0.82,
    'top_k': 32,
    'style': 'seraphine',
    'style_strength': 1.18
}

def text_to_speech(text: str) -> bytes:
    """文本转语音"""
    try:
        params = {'text': text, **VOICE_PARAMS}
        response = requests.get(VOICE_SERVICE_URL, params=params, timeout=60)
        if response.status_code == 200:
            return response.content
        else:
            print(f"❌ TTS 错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ TTS 异常: {e}")
        return None

def generate_voice_reply(user_text: str) -> str:
    """生成回复文本（简单版，实际由 OpenClaw AI 处理）"""
    # 这里只是占位符，真正的回复由 OpenClaw 生成
    return f"收到: {user_text}"

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', required=True, help='要转换为语音的文本')
    parser.add_argument('--output', default='/tmp/voice_reply.wav', help='输出文件路径')
    args = parser.parse_args()
    
    print(f"🎙️ 生成语音: {args.text[:50]}...")
    voice_data = text_to_speech(args.text)
    
    if voice_data:
        with open(args.output, 'wb') as f:
            f.write(voice_data)
        print(f"✅ 语音已保存: {args.output}")
    else:
        print("❌ 生成失败")
        sys.exit(1)
