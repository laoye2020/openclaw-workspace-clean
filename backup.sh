#!/bin/bash
# 🌱 豆芽配置一键备份脚本
# 用法: ./backup.sh [提交信息]

set -e

BACKUP_DIR="/home/laoye/.openclaw/workspace"
COMMIT_MSG="${1:-🔄 自动备份: $(date '+%Y-%m-%d %H:%M:%S')}"

echo "🌱 开始备份豆芽配置..."

cd "$BACKUP_DIR"

# 检查变更
if git diff --quiet && git diff --cached --quiet; then
    echo "✅ 没有变更需要备份"
    exit 0
fi

# 添加所有变更
git add -A

# 提交
git commit -m "$COMMIT_MSG"

# 推送到 GitHub
git push origin master

echo "✅ 备份完成！已推送到: https://github.com/laoye2020/openclaw-workspace"
echo "📊 提交: $(git rev-parse --short HEAD)"
echo "🕐 时间: $(date '+%Y-%m-%d %H:%M:%S')"
