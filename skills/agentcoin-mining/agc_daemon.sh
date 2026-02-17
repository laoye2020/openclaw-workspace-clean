#!/bin/bash
# AGC解题守护进程 - 每20秒执行一次

LOCK_FILE="/tmp/agc_solver_daemon.lock"
PID_FILE="/tmp/agc_solver_daemon.pid"
SCRIPT_DIR="/home/laoye/.openclaw/workspace/skills/agentcoin-mining"
SOLVER_SCRIPT="$SCRIPT_DIR/agc_solver.py"

# 检查是否已有实例在运行
check_running() {
    if [ -f "$PID_FILE" ]; then
        local old_pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
            echo "AGC solver already running (PID: $old_pid)"
            exit 0
        fi
    fi
}

# 清理函数
cleanup() {
    rm -f "$LOCK_FILE" "$PID_FILE"
    exit 0
}

trap cleanup SIGTERM SIGINT

# 主循环
main() {
    check_running
    
    # 写入PID
    echo $$ > "$PID_FILE"
    
    echo "[$(date '+%H:%M:%S')] AGC解题守护进程启动"
    
    while true; do
        # 执行解题器
        python3 "$SOLVER_SCRIPT" 2>&1 > /dev/null
        
        # 等待20秒
        sleep 20
    done
}

main
