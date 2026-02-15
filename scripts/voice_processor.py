#!/usr/bin/env python3
"""
Telegram 语音消息处理服务
下载语音文件并用 Whisper 转文字
"""

import os
import sys
import json
import requests
import tempfile
from pathlib import Path

# 添加虚拟环境路径
VENV_PATH = Path.home() / ".openclaw/workspace/venv-whisper"
sys.path.insert(0, str(VENV_PATH / "lib/python3.12/site-packages"))

import whisper

# Telegram Bot Token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

class VoiceProcessor:
    def __init__(self):
        # 加载 Whisper 模型（base 适合中文）
        print("正在加载 Whisper 模型...", file=sys.stderr)
        self.model = whisper.load_model("base")
        print("模型加载完成", file=sys.stderr)
    
    def download_voice(self, file_id):
        """从 Telegram 下载语音文件"""
        # 1. 获取文件路径
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile"
        response = requests.get(url, params={"file_id": file_id})
        data = response.json()
        
        if not data.get("ok"):
            raise Exception(f"获取文件失败: {data}")
        
        file_path = data["result"]["file_path"]
        
        # 2. 下载文件
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        voice_response = requests.get(download_url)
        
        # 3. 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(voice_response.content)
            return f.name
    
    def transcribe(self, audio_path, language='zh'):
        """转录音频为文字"""
        result = self.model.transcribe(audio_path, language=language)
        return result["text"]
    
    def process(self, file_id):
        """完整处理流程"""
        try:
            # 下载
            audio_path = self.download_voice(file_id)
            
            # 转录
            text = self.transcribe(audio_path)
            
            # 清理临时文件
            os.unlink(audio_path)
            
            return {"success": True, "text": text}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "需要 file_id 参数"}))
        sys.exit(1)
    
    file_id = sys.argv[1]
    processor = VoiceProcessor()
    result = processor.process(file_id)
    print(json.dumps(result, ensure_ascii=False))
