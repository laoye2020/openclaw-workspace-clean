#!/bin/bash
# 萨勒芬妮v2 语音合成 - 直接推理脚本

# 设置路径
EXP_DIR="/home/laoye/.openclaw/tools/seraphine-voice-v2/exp"
GPT_SOVITS_DIR="/home/laoye/.openclaw/tools/GPT-SoVITS"

# 模型路径
S1_MODEL="$EXP_DIR/s1/ckpt/epoch=199-step=1100.ckpt"
S2G_MODEL="$EXP_DIR/logs_s2_v1/G_233333333333.pth"
S2D_MODEL="$EXP_DIR/logs_s2_v1/D_233333333333.pth"

# 参考音频（用于音色克隆）
REF_WAV="$EXP_DIR/5-wav32k/segment_0000.wav"

# 检查模型
if [ ! -f "$S1_MODEL" ] || [ ! -f "$S2G_MODEL" ]; then
    echo "❌ 模型文件不存在"
    exit 1
fi

echo "🎙️ 萨勒芬妮v2 语音合成"
echo "======================="
echo "S1模型: $S1_MODEL"
echo "S2G模型: $S2G_MODEL"
echo "参考音频: $REF_WAV"
echo "======================="

# 进入项目目录
cd "$GPT_SOVITS_DIR" || exit 1
source venv/bin/activate
export PYTHONPATH="$GPT_SOVITS_DIR:$PYTHONPATH"

# 运行Python推理
python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS')
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS')

import torch
import soundfile as sf
from GPT_SoVITS.inference_webui import change_gpt_weights, change_sovits_weights, get_tts_wav

# 加载模型
print("📥 加载S1模型...")
change_gpt_weights('/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/s1/ckpt/epoch=199-step=1100.ckpt')

print("📥 加载S2模型...")
change_sovits_weights('/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/logs_s2_v1/G_233333333333.pth')

# 文本
text = "北国风光，千里冰封，万里雪飘。"
print(f"📝 文本: {text}")

# 生成
print("🔊 生成语音...")
ref_wav = '/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/5-wav32k/segment_0000.wav'

try:
    result = get_tts_wav(
        ref_wav_path=ref_wav,
        prompt_text="你好",
        prompt_language="中文",
        text=text,
        text_language="中文",
        how_to_cut="按句号切"
    )
    
    # 保存
    output_path = '/tmp/seraphine_v2_output.wav'
    sf.write(output_path, result[0], result[1])
    print(f"✅ 已保存: {output_path}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

PYTHON_SCRIPT

echo "======================="
echo "完成！"
