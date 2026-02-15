#!/bin/bash
# Polymarket 极速交易工具 - 启动脚本

echo "⚡ Polymarket 极速交易工具"
echo "=========================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -q streamlit py_clob_client requests web3 eth_account pandas

# 运行
echo ""
echo "🚀 启动中..."
echo "浏览器访问: http://localhost:8501"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

streamlit run app.py
