#!/usr/bin/env python3
"""
🎙️ Whisper 语音识别服务 - 常驻内存版
模型只加载一次，后续请求直接处理
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse

# 加载 Whisper
print("🔄 正在加载 Whisper 模型 (tiny)...")
import whisper
whisper_model = whisper.load_model("tiny")
print("✅ Whisper 模型已加载，服务就绪！")

class WhisperHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 简化日志输出
        pass
    
    def do_POST(self):
        if self.path == '/transcribe':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # 解析 multipart/form-data
                import io
                import re
                
                # 提取 boundary
                content_type = self.headers.get('Content-Type', '')
                boundary = re.search(r'boundary=([^;]+)', content_type)
                if not boundary:
                    self._send_error("No boundary found")
                    return
                
                boundary = boundary.group(1).strip()
                
                # 保存音频文件
                temp_file = tempfile.NamedTemporaryFile(suffix='.ogg', delete=False)
                temp_file.close()
                
                # 解析 multipart 数据，提取文件
                parts = post_data.split(b'--' + boundary.encode())
                for part in parts:
                    if b'Content-Disposition' in part and b'filename=' in part:
                        # 找到文件内容
                        header_end = part.find(b'\r\n\r\n')
                        if header_end != -1:
                            file_content = part[header_end + 4:].rstrip(b'\r\n')
                            with open(temp_file.name, 'wb') as f:
                                f.write(file_content)
                            break
                
                # 语音识别
                result = whisper_model.transcribe(temp_file.name, language='zh')
                text = result.get('text', '').strip()
                
                # 清理临时文件
                os.unlink(temp_file.name)
                
                # 返回结果
                self._send_json({'success': True, 'text': text})
                
            except Exception as e:
                self._send_error(str(e))
        else:
            self._send_error("Unknown endpoint")
    
    def do_GET(self):
        if self.path == '/health':
            self._send_json({'status': 'ok', 'model': 'tiny'})
        else:
            self._send_error("Unknown endpoint")
    
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, message):
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': False, 'error': message}).encode())

def main():
    port = 8007
    server = HTTPServer(('127.0.0.1', port), WhisperHandler)
    print(f"🎙️ Whisper 服务启动: http://127.0.0.1:{port}")
    print("   POST /transcribe - 语音识别")
    print("   GET  /health     - 健康检查")
    print("   按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        server.shutdown()

if __name__ == '__main__':
    main()
