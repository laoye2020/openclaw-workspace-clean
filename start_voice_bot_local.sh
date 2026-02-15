#!/bin/bash
# 🎙️ 启动豆芽双向语音对话系统 - 完全本地版

echo "🌱 启动双向语音对话系统（完全本地版）..."
echo ""

# 激活环境
source ~/.openclaw/workspace/voice-lab/scripts/activate.sh

# 检查语音服务
if ! curl -s http://localhost:8006/health > /dev/null; then
    echo "⚠️ 语音服务未启动，正在启动..."
    cd ~/.openclaw/workspace/voice-lab
    bash scripts/start_service.sh
    sleep 10
fi

echo "✅ 本地语音服务就绪"
echo "✅ 本地 Whisper 模型已加载"
echo ""
echo "🎙️ 启动 Telegram Bot..."
echo "   模式: 完全本地（无需 API Key）"
echo "   功能: 语音↔语音，文字↔语音"
echo ""

# 启动 Bot
cd ~/.openclaw/workspace
python3 voice_bot_local.py
