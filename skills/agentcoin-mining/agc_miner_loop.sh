#!/bin/bash

# AGC解题执行器 - 循环脚本
AGENT_ID=7039
SUBMITTED_FILE="/tmp/agc_submitted_ids.txt"
SUBMIT_SCRIPT="/home/laoye/.openclaw/workspace/skills/agentcoin-mining/submit.py"

# 创建去重文件（如果不存在）
touch "$SUBMITTED_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] AGC解题执行器已启动 (AGENT_ID: $AGENT_ID)"
echo "=================================================="

while true; do
    TIMESTAMP=$(date +%s)
    
    # 1. 获取题目状态
    STATUS_JSON=$(curl -s "https://api.agentcoin.site/api/mining/status" 2>/dev/null)
    PROBLEM_JSON=$(curl -s "https://api.agentcoin.site/api/problem/current?t=$TIMESTAMP" 2>/dev/null)
    
    # 2. 检查is_active字段
    IS_ACTIVE=$(echo "$STATUS_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('is_active','false'))" 2>/dev/null)
    
    if [ "$IS_ACTIVE" != "True" ] && [ "$IS_ACTIVE" != "true" ]; then
        # 静默结束，等待20秒
        sleep 20
        continue
    fi
    
    # 解析题目数据
    PROBLEM_ID=$(echo "$PROBLEM_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null)
    IS_ACTIVE_PROBLEM=$(echo "$PROBLEM_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('is_active','false'))" 2>/dev/null)
    PROBLEM_TEXT=$(echo "$PROBLEM_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('text',''))" 2>/dev/null)
    
    if [ -z "$PROBLEM_ID" ] || { [ "$IS_ACTIVE_PROBLEM" != "True" ] && [ "$IS_ACTIVE_PROBLEM" != "true" ]; }; then
        sleep 20
        continue
    fi
    
    # 3. 检查去重文件
    if grep -q "^${PROBLEM_ID}$" "$SUBMITTED_FILE" 2>/dev/null; then
        # 已提交过，静默
        sleep 20
        continue
    fi
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 发现新题目: #$PROBLEM_ID"
    echo "题目: $PROBLEM_TEXT"
    
    # 4. 解题 - 提取N值并计算
    # 解析题目中的N值 (sum of all positive integers k ≤ N such that...)
    N_VALUE=$(echo "$PROBLEM_TEXT" | grep -oE '[0-9]+' | tail -1)
    
    if [ -z "$N_VALUE" ]; then
        echo "无法解析N值"
        message send --target 8270250565 --message "❌ AGC失败 | 题号#$PROBLEM_ID | 原因: 无法解析题目中的N值"
        sleep 20
        continue
    fi
    
    # 使用容斥原理计算答案
    # sum of all positive integers k ≤ N such that k is divisible by 3 or 5, but not by 15
    # 答案 = sum(3的倍数) + sum(5的倍数) - 2×sum(15的倍数)
    
    ANSWER=$(python3 << EOF
import math

N = $N_VALUE

# 计算能被3整除但不能被15整除的数的和
def sum_divisible_by(n, N):
    k = N // n
    return n * k * (k + 1) // 2

# sum(3的倍数) + sum(5的倍数) - 2*sum(15的倍数)
# 原因：被15整除的数同时被3和5整除，被算了两次，需要减去两次
total = sum_divisible_by(3, N) + sum_divisible_by(5, N) - 2 * sum_divisible_by(15, N)
print(total)
EOF
)
    
    echo "计算结果: N=$N_VALUE, 答案=$ANSWER"
    
    # 5. 提交答案
    cd /home/laoye/.openclaw/workspace/skills/agentcoin-mining
    SUBMIT_OUTPUT=$(AGC_PRIVATE_KEY="0xad07adbcc4981f3b13f8ab5694ae11500ea019d12d3cece54c9c37fdfa945534" python3 submit.py "$PROBLEM_ID" "$ANSWER" 2>&1)
    SUBMIT_EXIT_CODE=$?
    
    echo "提交输出: $SUBMIT_OUTPUT"
    
    # 6. 处理结果
    if [ $SUBMIT_EXIT_CODE -eq 0 ]; then
        # 检查是否成功 - submit.py输出格式: {'tx':..., 'status':..., 'gasUsed':...}
        TX_HASH=$(echo "$SUBMIT_OUTPUT" | python3 -c "import sys,json; d=eval(sys.stdin.read()); print(d.get('tx',''))" 2>/dev/null)
        STATUS=$(echo "$SUBMIT_OUTPUT" | python3 -c "import sys,json; d=eval(sys.stdin.read()); print(d.get('status','0'))" 2>/dev/null)
        GAS=$(echo "$SUBMIT_OUTPUT" | python3 -c "import sys,json; d=eval(sys.stdin.read()); print(d.get('gasUsed',''))" 2>/dev/null)
        
        if [ "$STATUS" == "1" ]; then
            # 成功
            TX_PREFIX="${TX_HASH:0:10}"
            echo "$PROBLEM_ID" >> "$SUBMITTED_FILE"
            openclaw message send --target 8270250565 --message "✅ AGC成功 | 题号#$PROBLEM_ID | 答案$ANSWER | tx前缀$TX_PREFIX | gas$GAS"
        else
            # 提交返回但状态不为1
            openclaw message send --target 8270250565 --message "❌ AGC失败 | 题号#$PROBLEM_ID | 原因:交易状态失败 status=$STATUS"
        fi
    else
        # 提交脚本执行失败
        ERROR_MSG=$(echo "$SUBMIT_OUTPUT" | head -100 | tr -d '\n' | cut -c1-200)
        openclaw message send --target 8270250565 --message "❌ AGC失败 | 题号#$PROBLEM_ID | 原因:提交脚本执行失败 - $ERROR_MSG"
    fi
    
    echo "=================================================="
    
    # 等待20秒
    sleep 20
done
