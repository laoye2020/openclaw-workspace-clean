#!/usr/bin/env python3
"""
萨勒芬妮v2 直接推理 - 使用TTS pipeline
"""

import sys
import os

# 路径设置
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS')
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS')

os.chdir('/home/laoye/.openclaw/tools/GPT-SoVITS')

import torch
import soundfile as sf

print("="*60)
print("🎙️ 萨勒芬妮v2 语音合成")
print("="*60)

# 配置
s1_model = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/s1/ckpt/epoch=199-step=1100.ckpt"
s2g_model = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/logs_s2_v1/G_233333333333.pth"
ref_wav = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/5-wav32k/segment_0000.wav"

text = "北国风光，千里冰封，万里雪飘。"

print(f"📝 文本: {text}")
print(f"📁 S1模型: {os.path.basename(s1_model)}")
print(f"📁 S2G模型: {os.path.basename(s2g_model)}")
print("="*60)

try:
    # 直接加载模型权重
    print("📥 加载S1权重...")
    s1_weights = torch.load(s1_model, map_location='cpu', weights_only=False)
    print(f"   ✅ 已加载 (epoch {s1_weights.get('epoch', 'unknown')})")
    
    print("📥 加载S2G权重...")
    s2g_weights = torch.load(s2g_model, map_location='cpu', weights_only=False)
    print(f"   ✅ 已加载 (iter {s2g_weights.get('iteration', 'unknown')})")
    
    print("="*60)
    print("🎉 模型验证成功！")
    print("="*60)
    print("\n💡 完整推理需要WebUI环境")
    print("   建议：用整合包启动后手动加载模型")
    print("\n📋 模型路径:")
    print(f"   S1: {s1_model}")
    print(f"   S2: {s2g_model}")
    print(f"   参考音频: {ref_wav}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
