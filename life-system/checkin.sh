#!/bin/bash
# 打卡记录脚本 - 记录每日打卡状态

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
CHECKIN_FILE="/home/laoye/.openclaw/workspace/life-system/checkin-log.md"
PUNISHMENT_FILE="/home/laoye/.openclaw/workspace/life-system/punishment-pool.md"

# 参数解析
ACTION=$1  # start/complete/skip
ITEM=$2    # meditation-morning/face/workout/meditation-evening

# 根据项目确定惩罚时间
case $ITEM in
    meditation-morning)
        PUNISHMENT=15
        ITEM_NAME="起床打坐"
        ;;
    face)
        PUNISHMENT=5
        ITEM_NAME="脸部按摩"
        ;;
    workout)
        PUNISHMENT=60
        ITEM_NAME="晨练"
        ;;
    meditation-evening)
        PUNISHMENT=15
        ITEM_NAME="睡前打坐"
        ;;
    *)
        echo "未知项目: $ITEM"
        exit 1
        ;;
esac

# 记录打卡
if [ "$ACTION" == "start" ]; then
    echo "[$TIME] 🟡 $ITEM_NAME 开始" >> $CHECKIN_FILE
    echo "✅ 已记录开始时间"
elif [ "$ACTION" == "complete" ]; then
    echo "[$TIME] ✅ $ITEM_NAME 完成" >> $CHECKIN_FILE
    echo "🎉 打卡成功！"
elif [ "$ACTION" == "skip" ]; then
    echo "[$TIME] ❌ $ITEM_NAME 跳过（惩罚: ${PUNISHMENT}min）" >> $CHECKIN_FILE
    # 加入惩罚池
    echo "$DATE $ITEM_NAME ${PUNISHMENT}" >> $PUNISHMENT_FILE
    echo "⚠️ 已记录惩罚，周末+${PUNISHMENT}分钟"
else
    echo "用法: $0 [start|complete|skip] [项目名]"
    echo "项目: meditation-morning, face, workout, meditation-evening"
fi
