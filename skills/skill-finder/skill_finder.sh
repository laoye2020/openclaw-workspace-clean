#!/bin/bash
# 🔍 智能技能发现助手
# 用法: ./skill_finder.sh "需求描述"

if [ -z "$1" ]; then
    echo "🔍 技能发现助手"
    echo "用法: ./skill_finder.sh <需求关键词>"
    echo ""
    echo "示例:"
    echo "  ./skill_finder.sh '语音识别'"
    echo "  ./skill_finder.sh 'PDF编辑'"
    echo "  ./skill_finder.sh '天气查询'"
    exit 1
fi

KEYWORD="$1"
echo "🔍 正在搜索与 '$KEYWORD' 相关的技能..."
echo "=========================================="

# 使用 clawhub 搜索
npx clawhub search "$KEYWORD" --limit 10

echo ""
echo "💡 安装命令:"
echo "  npx clawhub install <技能名称>"
