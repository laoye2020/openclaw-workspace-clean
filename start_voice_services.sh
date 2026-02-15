#!/bin/bash
# 🎙️ 启动完整语音服务（Whisper + CosyVoice）

echo "🌱 启动豆芽语音服务..."

# 激活环境
source ~/.openclaw/workspace/voice-lab/scripts/activate.sh

# 1. 检查 CosyVoice 服务
if ! curl -s http://localhost:8006/health > /dev/null; then
    echo "🎙️ 启动 CosyVoice 服务..."
    cd ~/.openclaw/workspace/voice-lab
    bash scripts/start_service.sh
    sleep 5
fi
echo "✅ CosyVoice 就绪"

# 2. 检查 Whisper 服务
if ! curl -s http://127.0.0.1:8007/health > /dev/null; then
    echo "🎙️ 启动 Whisper 常驻服务..."
    cd ~/.openclaw/workspace
    nohup python3 whisper_service.py > /tmp/whisper_service.log 2>&1 &
    echo $! > /tmp/whisper_service.pid
    
    # 等待服务就绪
    for i in {1..30}; do
        if curl -s http://127.0.0.1:8007/health > /dev/null; then
            echo "✅ Whisper 服务就绪"
            break
        fi
        sleep 1
    done
else
    echo "✅ Whisper 服务已在运行"
fi

echo ""
echo "🎉 所有语音服务已启动！"
echo "   - CosyVoice: http://localhost:8006"
echo "   - Whisper:   http://127.0.0.1:8007"
echo ""
echo "💡 使用说明:"
echo "   发语音给我，我会用萨勒芬妮声音回复！"
echo ""
echo "🛑 停止服务:"
echo "   - CosyVoice: ~/.openclaw/workspace/voice-lab/scripts/stop_service.sh"
echo "   - Whisper:   kill \$(cat /tmp/whisper_service.pid)"
