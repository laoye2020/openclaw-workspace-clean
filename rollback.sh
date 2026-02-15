#!/bin/bash
# 🌱 豆芽历史版本回滚脚本

set -e

WORKSPACE="/home/laoye/.openclaw/workspace"

cd "$WORKSPACE"

show_help() {
    echo "🌱 豆芽版本回滚工具"
    echo ""
    echo "用法:"
    echo "  ./rollback.sh list          # 查看所有历史版本"
    echo "  ./rollback.sh preview <id>  # 预览某个版本"
    echo "  ./rollback.sh restore <id>  # 回滚到指定版本"
    echo "  ./rollback.sh last          # 回滚到上一个版本"
    echo "  ./rollback.sh reset         # 强制重置到最新（慎用）"
    echo ""
    echo "示例:"
    echo "  ./rollback.sh restore cee9f14   # 回滚到初始配置"
}

list_versions() {
    echo "📜 历史版本列表："
    echo ""
    git log --oneline --all --decorate | head -20
    echo ""
    echo "💡 使用 ./rollback.sh restore <commit-id> 回滚到指定版本"
}

preview_version() {
    local commit="$1"
    if [ -z "$commit" ]; then
        echo "❌ 错误：需要指定版本ID"
        echo "用法: ./rollback.sh preview cee9f14"
        exit 1
    fi
    
    echo "👀 预览版本 $commit 的内容变更："
    echo ""
    git show --stat "$commit"
}

restore_version() {
    local commit="$1"
    if [ -z "$commit" ]; then
        echo "❌ 错误：需要指定版本ID"
        echo "用法: ./rollback.sh restore cee9f14"
        exit 1
    fi
    
    echo "⚠️  警告：这将回滚到版本 $commit"
    echo "📋 当前修改将被暂存（stash），可以稍后恢复"
    echo ""
    read -p "确定要继续吗？(yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "❌ 已取消"
        exit 0
    fi
    
    # 保存当前修改（如果有）
    if ! git diff --quiet HEAD; then
        echo "💾 保存当前修改到 stash..."
        git stash push -m "回滚前自动保存 $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    echo "🔄 回滚到 $commit..."
    git checkout "$commit" -- .
    
    echo "💾 创建回滚后的提交..."
    git add -A
    git commit -m "⏪ 回滚到版本 $commit

回滚时间: $(date '+%Y-%m-%d %H:%M:%S')
原版本: $commit"
    
    echo ""
    echo "✅ 回滚完成！"
    echo "📝 新提交: $(git rev-parse --short HEAD)"
    echo ""
    echo "💡 如果后悔了，可以再次回滚到之前的版本"
    echo "💡 查看 stash: git stash list"
}

rollback_last() {
    echo "🔄 回滚到上一个版本..."
    git log --oneline -2
    echo ""
    
    local last_commit=$(git log --oneline -2 | tail -1 | awk '{print $1}')
    restore_version "$last_commit"
}

reset_hard() {
    echo "⚠️  警告：这将强制丢弃所有本地修改！"
    echo ""
    read -p "确定要强制重置吗？(yes/no): " confirm
    
    if [ "$confirm" == "yes" ]; then
        git fetch origin
        git reset --hard origin/master
        echo "✅ 已强制重置到远程最新版本"
    else
        echo "❌ 已取消"
    fi
}

# 主逻辑
case "${1:-help}" in
    list|ls)
        list_versions
        ;;
    preview|show|view)
        preview_version "$2"
        ;;
    restore|rollback|checkout)
        restore_version "$2"
        ;;
    last|prev)
        rollback_last
        ;;
    reset|hard)
        reset_hard
        ;;
    help|*)
        show_help
        ;;
esac
