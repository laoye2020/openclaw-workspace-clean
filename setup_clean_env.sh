#!/bin/bash
# 创建全新的 GPT-SoVITS 虚拟环境

echo "🚀 创建全新的 GPT-SoVITS 环境..."

# 创建conda环境
conda create -n gptsovits python=3.10 -y

# 激活
source $(conda info --base)/etc/profile.d/conda.sh
conda activate gptsovits

# 安装 PyTorch（匹配CUDA 12.1）
pip install torch==2.5.1+cu121 torchaudio==2.5.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

# 安装其他依赖
pip install transformers==4.40.0
pip install peft==0.4.0
pip install gradio==3.50.2
pip install fast_langdetect
pip install split_lang

# 克隆 GPT-SoVITS
cd ~
git clone https://github.com/RVC-Boss/GPT-SoVITS.git GPT-SoVITS-clean

# 下载预训练模型
mkdir -p GPT-SoVITS-clean/GPT_SoVITS/pretrained_models
cd GPT-SoVITS-clean/GPT_SoVITS/pretrained_models

# 下载必要的模型
echo "📥 下载预训练模型..."
# (这里可以用huggingface-cli或者手动下载)

echo "✅ 环境创建完成！"
echo "激活命令: conda activate gptsovits"
