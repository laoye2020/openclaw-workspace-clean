#!/bin/bash
# 上传日历到服务器的脚本
# 需要输入密码: @Qwer092319

SERVER="root@47.107.58.190"
REMOTE_PATH="/usr/share/nginx/html/calendar.ics"
LOCAL_PATH="$HOME/.openclaw/workspace/life-system/calendar.ics"

echo "正在上传日历文件..."
scp "$LOCAL_PATH" "$SERVER:$REMOTE_PATH"

if [ $? -eq 0 ]; then
    echo "✅ 上传成功！"
    echo "日历已更新: https://laoye2025.top/calendar.ics"
else
    echo "❌ 上传失败，请检查网络或密码"
fi
