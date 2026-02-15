#!/bin/bash
# 🎙️ 启动豆芽双向语音对话系统

echo "🌱 启动双向语音对话系统..."

# 激活环境
source ~/.openclaw/workspace/voice-lab/scripts/activate.sh

# 设置环境变量（从 .env 加载）
if [ -f ~/.openclaw/.env ]; then
    export $(grep -v '^#' ~/.openclaw/.env | xargs)
fi

# 检查语音服务
if ! curl -s http://localhost:8006/health > /dev/null; then
    echo "⚠️ 语音服务未启动，正在启动..."
    cd ~/.openclaw/workspace/voice-lab
    bash scripts/start_service.sh
    sleep 10
fi

echo "✅ 语音服务就绪"
echo "🎙️ 启动 Telegram Bot..."
echo ""

# 启动 Bot
cd ~/.openclaw/workspace
python3 voice_bot.py
