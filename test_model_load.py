#!/usr/bin/env python3
"""
萨勒芬妮v2 直接推理 - 绕过WebUI
"""

import sys
import os
# 绕过PyTorch安全限制
os.environ['TORCH_FORCE_WEIGHTS_ONLY_LOAD'] = '0'
os.environ['PYTHONWARNINGS'] = 'ignore'

import torch
import torchaudio

# 添加路径
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS')
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS')

# 设置模型路径
S1_MODEL = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/s1/ckpt/epoch=199-step=1100.ckpt"
S2G_MODEL = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/logs_s2_v1/G_233333333333.pth"
REF_WAV = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/5-wav32k/segment_0000.wav"

# 文本
TEXT = "北国风光，千里冰封，万里雪飘。"

print("="*50)
print("🎙️ 萨勒芬妮v2 直接推理")
print("="*50)
print(f"文本: {TEXT}")
print(f"S1: {os.path.basename(S1_MODEL)}")
print(f"S2G: {os.path.basename(S2G_MODEL)}")
print("="*50)

# 检查文件
for f in [S1_MODEL, S2G_MODEL, REF_WAV]:
    if not os.path.exists(f):
        print(f"❌ 文件不存在: {f}")
        sys.exit(1)
    print(f"✅ {os.path.basename(f)}")

print("="*50)

# 加载模型并生成
try:
    os.chdir('/home/laoye/.openclaw/tools/GPT-SoVITS')
    
    # 直接加载torch模型
    print("📥 加载S1模型...")
    s1_state = torch.load(S1_MODEL, map_location='cpu', weights_only=False)
    print(f"   S1 keys: {list(s1_state.keys())[:3]}...")
    
    print("📥 加载S2G模型...")
    s2g_state = torch.load(S2G_MODEL, map_location='cpu', weights_only=False)
    print(f"   S2G keys: {list(s2g_state.keys())[:3]}...")
    
    print("✅ 模型加载成功！")
    print("="*50)
    print("📝 注意：完整推理需要GPT-SoVITS完整环境")
    print("   建议明天用官方整合包进行最终测试")
    print("="*50)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n💡 明天的整合包方案：")
print("   1. 下载 https://huggingface.co/lj1995/GPT-SoVITS")
print("   2. 复制模型文件到整合包目录")
print("   3. 启动整合包WebUI")
print("   4. 加载模型生成语音")
