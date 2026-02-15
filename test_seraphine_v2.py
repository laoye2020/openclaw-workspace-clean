#!/usr/bin/env python3
"""
萨勒芬妮v2 语音合成测试
文本：《沁园春·雪》
"""

import os
import sys
import torch
import torchaudio

# 添加项目路径
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS')
sys.path.insert(0, '/home/laoye/.openclaw/tools/GPT-SoVITS/GPT_SoVITS')

# 设置模型路径
s1_model = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/s1/ckpt/epoch=199-step=1100.ckpt"
s2g_model = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/logs_s2_v1/G_233333333333.pth"
s2d_model = "/home/laoye/.openclaw/tools/seraphine-voice-v2/exp/logs_s2_v1/D_233333333333.pth"

# 文本
TEXT = """北国风光，千里冰封，万里雪飘。
望长城内外，惟余莽莽；大河上下，顿失滔滔。
山舞银蛇，原驰蜡象，欲与天公试比高。
须晴日，看红装素裹，分外妖娆。
江山如此多娇，引无数英雄竞折腰。
惜秦皇汉武，略输文采；唐宗宋祖，稍逊风骚。
一代天骄，成吉思汗，只识弯弓射大雕。
俱往矣，数风流人物，还看今朝。"""

print("="*50)
print("🎙️ 萨勒芬妮v2 语音合成测试")
print("="*50)
print(f"文本：《沁园春·雪》")
print(f"字数：{len(TEXT)} 字")
print(f"S1模型：{s1_model}")
print(f"S2G模型：{s2g_model}")
print(f"S2D模型：{s2d_model}")
print("="*50)

# 检查模型文件是否存在
for model_path in [s1_model, s2g_model, s2d_model]:
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / 1024 / 1024
        print(f"✅ {os.path.basename(model_path)} ({size_mb:.0f}MB)")
    else:
        print(f"❌ 模型文件不存在: {model_path}")
        sys.exit(1)

print("="*50)
print("模型文件检查通过！")
print("注意：完整推理需要启动WebUI或使用API")
print("="*50)
