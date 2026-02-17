#!/bin/bash
# AGC解题守护进程监控器 - 确保守护进程一直在运行

PID_FILE="/tmp/agc_solver_daemon.pid"
DAEMON_SCRIPT="/home/laoye/.openclaw/workspace/skills/agentcoin-mining/agc_daemon.sh"

# 检查守护进程是否运行
check_and_start() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            # 守护进程正在运行
            exit 0
        fi
    fi
    
    # 启动守护进程
    nohup "$DAEMON_SCRIPT" > /tmp/agc_daemon.log 2>&1 &
    echo "[$(date '+%H:%M:%S')] AGC守护进程已启动"
}

check_and_start
