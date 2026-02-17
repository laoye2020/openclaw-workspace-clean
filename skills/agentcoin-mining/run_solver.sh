#!/bin/bash
# AGC解题执行器 - 包装脚本
# 设置环境并执行

cd /home/laoye/.openclaw/workspace/skills/agentcoin-mining

# 设置Python路径（如果需要）
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 执行解题器
python3 agc_solver.py 2>&1
