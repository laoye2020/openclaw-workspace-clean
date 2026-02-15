#!/usr/bin/env python3
"""
萨勒芬妮v2 语音合成测试
直接使用加载的模型生成语音
"""

import sys
import os

# 设置环境变量
os.environ['bert_path'] = '/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large'
os.environ['cnhubert_base_path'] = '/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS/pretrained_models/chinese-hubert-base'

# 设置路径
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS')
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS')
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS/eres2net')

os.chdir('/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS')

print("="*60)
print("🎙️ 萨勒芬妮v2 语音合成测试")
print("="*60)

try:
    import torch
    import soundfile as sf
    
    # 加载模型
    print("📥 加载S1模型...")
    s1_path = '/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/s1/ckpt/seraphine_v2_s1_converted.ckpt'
    s1_ckpt = torch.load(s1_path, map_location='cpu', weights_only=False)
    print(f"   ✅ S1 (epoch {s1_ckpt.get('epoch', 'unknown')})")
    
    print("📥 加载S2模型...")
    s2_path = '/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/logs_s2_v1/G_233333333333.pth'
    s2_ckpt = torch.load(s2_path, map_location='cpu', weights_only=False)
    print(f"   ✅ S2 (iter {s2_ckpt.get('iteration', 'unknown')})")
    
    # 加载参考音频
    print("📥 加载参考音频...")
    ref_wav = '/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/5-wav32k/segment_0000.wav'
    ref_audio, ref_sr = sf.read(ref_wav)
    print(f"   ✅ {len(ref_audio)} 样本 @ {ref_sr}Hz")
    
    print("="*60)
    print("🎉 模型加载成功！")
    print("="*60)
    
    # 显示文本
    text = "北国风光，千里冰封，万里雪飘。"
    print(f"\n📝 待合成文本: {text}")
    print("\n💡 由于缺少完整TTS pipeline，目前仅验证模型可加载")
    print("   完整推理需通过WebUI或完整环境")
    
    print("\n📋 模型信息:")
    print(f"   S1权重: {s1_path}")
    print(f"   S2权重: {s2_path}")
    print(f"   参考音频: {ref_wav}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
