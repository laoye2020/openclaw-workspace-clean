#!/usr/bin/env python3
"""AGC解题执行器 - 每20秒循环"""
import time
import json
import requests
import os
import subprocess
import sys
from datetime import datetime

# 配置
STATUS_URL = "https://api.agentcoin.site/api/mining/status"
PROBLEM_URL_TEMPLATE = "https://api.agentcoin.site/api/problem/current?t={}"
SUBMITTED_FILE = "/tmp/agc_submitted_ids.txt"
TELEGRAM_TARGET = "8270250565"
PRIVATE_KEY = os.getenv("AGC_PRIVATE_KEY", "")
SUBMIT_DIR = "/home/laoye/.openclaw/workspace/skills/agentcoin-mining"

def log(msg):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}", flush=True)

def get_submitted_ids():
    """获取已提交的题目ID集合"""
    if not os.path.exists(SUBMITTED_FILE):
        return set()
    with open(SUBMITTED_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def add_submitted_id(pid):
    """添加已提交题目ID"""
    with open(SUBMITTED_FILE, 'a') as f:
        f.write(f"{pid}\n")

def fetch_json(url):
    """获取JSON数据"""
    try:
        resp = requests.get(url, timeout=15)
        return resp.json()
    except Exception as e:
        return None

def solve_tiling_problem(agent_id):
    """解决铺砖问题
    
    题目：Given AGENT_ID = {AGENT_ID}, let N = (AGENT_ID mod 100) + 50.
    Compute the number of ways to tile a 2×N rectangle using 1×2 dominoes and 2×2 squares.
    Then, compute the sum of the digits of that number when expressed in base 2 (binary).
    """
    # 计算 N
    N = (agent_id % 100) + 50
    log(f"AGENT_ID={agent_id}, N={N}")
    
    # 动态规划计算铺砖方式
    # dp[i] = 铺2xi矩形的方式数
    # 递推: dp[i] = dp[i-1] + 2*dp[i-2]
    #   - 竖放一个1x2: dp[i-1]
    #   - 横放两个1x2: dp[i-2]
    #   - 放一个2x2: dp[i-2]
    
    if N == 0:
        ways = 1
    elif N == 1:
        ways = 1
    else:
        dp = [0] * (N + 1)
        dp[0] = 1
        dp[1] = 1
        for i in range(2, N + 1):
            dp[i] = dp[i-1] + 2 * dp[i-2]
        ways = dp[N]
    
    log(f"铺砖方式数: {ways}")
    
    # 计算二进制中1的个数
    binary_ones = bin(ways).count('1')
    log(f"二进制1的个数: {binary_ones}")
    
    return binary_ones

def submit_answer(problem_id, answer):
    """提交答案到区块链"""
    cmd = [
        "python3", "submit.py",
        str(problem_id),
        str(answer)
    ]
    env = os.environ.copy()
    env["AGC_PRIVATE_KEY"] = PRIVATE_KEY
    
    try:
        result = subprocess.run(
            cmd,
            cwd=SUBMIT_DIR,
            capture_output=True,
            text=True,
            env=env,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        log(f"提交输出: {output[:500]}")
        
        # 解析返回的JSON
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    data = json.loads(line)
                    return {
                        'status': 1 if data.get('status') == 1 else 0,
                        'tx_hash': data.get('tx', ''),
                        'gas_used': data.get('gasUsed', 0)
                    }
                except:
                    pass
        
        return {'status': 0, 'error': output[:200]}
    except Exception as e:
        return {'status': 0, 'error': str(e)}

def main():
    log("="*50)
    log("AGC解题执行器启动")
    log("="*50)
    
    while True:
        loop_start = time.time()
        
        try:
            # ===== 第1步：读取API =====
            log("📡 读取API...")
            status = fetch_json(STATUS_URL)
            problem = fetch_json(PROBLEM_URL_TEMPLATE.format(int(time.time())))
            
            if not status or not problem:
                log("⚠️ API获取失败，等待下次循环")
                time.sleep(max(0, 20 - (time.time() - loop_start)))
                continue
            
            problem_id = problem.get('problem_id')
            is_active = problem.get('is_active', False)
            
            log(f"题目ID: {problem_id}, is_active: {is_active}")
            
            # ===== 第2步：检查状态 =====
            if not is_active:
                log("⏸️ is_active=false，静默等待...")
                time.sleep(max(0, 20 - (time.time() - loop_start)))
                continue
            
            # ===== 第3步：去重检查 =====
            submitted = get_submitted_ids()
            if str(problem_id) in submitted:
                log(f"✓ 题目#{problem_id}已提交过，跳过")
                time.sleep(max(0, 20 - (time.time() - loop_start)))
                continue
            
            log(f"🎯 发现新活跃题目 #{problem_id}！")
            
            # ===== 第4步：解题 =====
            log("🧮 开始解题...")
            try:
                # AGENT_ID使用current_problem_id
                agent_id = status.get('current_problem_id', problem_id)
                answer = solve_tiling_problem(agent_id)
                log(f"✓ 解题完成，答案: {answer}")
            except Exception as e:
                error_msg = f"解题异常: {e}"
                log(f"❌ {error_msg}")
                # 发送失败消息
                msg = f"❌ AGC失败 | 题号#{problem_id} | 原因{error_msg}"
                print(f"MSG|{TELEGRAM_TARGET}|{msg}", flush=True)
                time.sleep(max(0, 20 - (time.time() - loop_start)))
                continue
            
            # ===== 第5步：提交 =====
            log("📤 提交答案...")
            result = submit_answer(problem_id, answer)
            
            # ===== 第6步：结果处理 =====
            if result.get('status') == 1:
                # 成功
                tx_hash = result.get('tx_hash', 'unknown')
                gas_used = result.get('gas_used', 0)
                
                # 记录已提交
                add_submitted_id(problem_id)
                
                # 发送成功消息
                msg = f"✅ AGC成功 | 题号#{problem_id} | 答案{answer} | tx前缀{tx_hash[:10]} | gas{gas_used}"
                log(f"✅ 提交成功!")
                print(f"MSG|{TELEGRAM_TARGET}|{msg}", flush=True)
            else:
                # 失败
                error = result.get('error', '未知错误')
                msg = f"❌ AGC失败 | 题号#{problem_id} | 原因{error}"
                log(f"❌ 提交失败: {error}")
                print(f"MSG|{TELEGRAM_TARGET}|{msg}", flush=True)
            
        except Exception as e:
            log(f"💥 循环异常: {e}")
        
        # 维持20秒周期
        elapsed = time.time() - loop_start
        sleep_time = max(0, 20 - elapsed)
        if sleep_time > 0:
            log(f"⏳ 等待 {sleep_time:.1f}秒...")
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()
