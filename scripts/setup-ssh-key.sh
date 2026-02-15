#!/bin/bash
# SSH 免密登录配置脚本
# 阿里云服务器: 47.107.58.190
# 密码: @Qwer092319

SERVER="47.107.58.190"
USER="root"
PASSWORD="@Qwer092319"

echo "🔐 配置 SSH 免密登录到阿里云服务器..."
echo "服务器: $SERVER"
echo ""

# 1. 确保密钥存在
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo "❌ 未找到 SSH 公钥，先生成..."
    ssh-keygen -t rsa -b 4096 -C "douya@openclaw" -f ~/.ssh/id_rsa -N ""
fi

echo "📋 公钥内容:"
cat ~/.ssh/id_rsa.pub
echo ""

# 2. 复制公钥到服务器（使用 sshpass）
echo "📤 正在复制公钥到服务器..."
sshpass -p "$PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no "$USER@$SERVER"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SSH 免密登录配置成功！"
    echo ""
    echo "🧪 测试连接..."
    ssh "$USER@$SERVER" "echo '连接成功！服务器时间:' \$(date)"
    echo ""
    echo "📅 测试日历上传..."
    scp ~/.openclaw/workspace/life-system/calendar.ics "$USER@$SERVER:/usr/share/nginx/html/calendar.ics"
    if [ $? -eq 0 ]; then
        echo "✅ 日历上传成功！"
        echo "📱 小米手机将自动同步更新"
    else
        echo "❌ 日历上传失败"
    fi
else
    echo "❌ 配置失败，请检查密码或网络"
fi
