#!/bin/bash
# 豆芽自动备份脚本 - 由 cron 调用

cd /home/laoye/.openclaw/workspace

# 生成带日期的提交信息
DATE=$(date '+%Y-%m-%d')
./backup.sh "🤖 自动每日备份 $DATE"
