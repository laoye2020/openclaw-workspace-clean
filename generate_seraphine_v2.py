#!/usr/bin/env python3
"""
萨勒芬妮v2 语音合成 - 完整推理
绕过weights_only安全限制
"""

import os
import sys

# 设置环境
os.chdir('/home/laoye/.openclaw/tools/GPT-SoVITS')
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS')
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS')

# 模型路径
S1_MODEL = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/s1/ckpt/epoch=199-step=1100.ckpt"
S2G_MODEL = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/logs_s2_v1/G_233333333333.pth"
S2D_MODEL = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/logs_s2_v1/D_233333333333.pth"
REF_WAV = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/5-wav32k/segment_0000.wav"

# 文本
TEXT = "北国风光，千里冰封，万里雪飘。望长城内外，惟余莽莽；大河上下，顿失滔滔。"

print("="*60)
print("🎙️ 萨勒芬妮v2 语音合成")
print("="*60)
print(f"📝 文本: {TEXT[:30]}...")
print("="*60)

try:
    import torch
    import soundfile as sf
    
    # 关键：用weights_only=False加载（我们信任自己的模型）
    print("📥 加载S1模型...")
    s1_checkpoint = torch.load(S1_MODEL, map_location='cpu', weights_only=False)
    print(f"   ✅ S1 loaded (epoch {s1_checkpoint.get('epoch', 'unknown')})")
    
    print("📥 加载S2G模型...")
    s2g_checkpoint = torch.load(S2G_MODEL, map_location='cpu', weights_only=False)
    print(f"   ✅ S2G loaded (iter {s2g_checkpoint.get('iteration', 'unknown')})")
    
    print("="*60)
    
    # 加载GPT-SoVITS推理模块
    print("🔧 初始化推理模块...")
    from inference_webui import change_gpt_weights, change_sovits_weights, get_tts_wav
    
    # 加载模型到推理引擎
    print("📥 加载模型到推理引擎...")
    change_gpt_weights(S1_MODEL)
    change_sovits_weights(S2G_MODEL)
    
    print("🔊 生成语音...")
    result = get_tts_wav(
        ref_wav_path=REF_WAV,
        prompt_text="你好",
        prompt_language="中文",
        text=TEXT,
        text_language="中文",
        how_to_cut="按句号切"
    )
    
    # 保存
    output_path = '/tmp/seraphine_v2_qinyuanchunxue.wav'
    sf.write(output_path, result[0], result[1])
    
    print("="*60)
    print(f"✅ 生成成功！")
    print(f"📁 保存到: {output_path}")
    print(f"📊 样本数: {len(result[0])}")
    print("="*60)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 建议: 使用官方整合包进行推理")
