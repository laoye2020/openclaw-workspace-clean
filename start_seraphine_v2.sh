#!/bin/bash
# 萨勒芬妮v2 整合包启动脚本

cd ~/下载/GPT-SoVITS-v2pro/GPT-SoVITS-v2pro-20250604

# 使用系统Python启动WebUI
export PYTHONPATH=$(pwd):$PYTHONPATH

# 启动API服务
python3 -c "
import sys
sys.path.insert(0, '.')
sys.path.insert(0, './GPT_SoVITS')

from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config

# 配置
tts_config = TTS_Config('GPT_SoVITS/configs/tts_infer.yaml')
tts_pipeline = TTS(tts_config)

print('🎙️ 萨勒芬妮v2 加载成功！')
print('模型路径:')
print('  S1: GPT_weights_v2/seraphine_v2_s1.ckpt')
print('  S2: SoVITS_weights_v2/seraphine_v2_s2.pth')
" 2>&1