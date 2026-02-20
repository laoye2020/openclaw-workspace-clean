#!/usr/bin/env python3
"""
AGC 自动解题执行器
每20秒检查一次题目，自动求解并提交
"""

import requests
import time
import os
import json
import subprocess
from datetime import datetime

# 配置
SUBMITTED_IDS_FILE = "/tmp/agc_submitted_ids.txt"
TELEGRAM_CHAT_ID = "8270250565"
AGENTCOIN_API_BASE = "https://api.agentcoin.site/api"
SUBMIT_SCRIPT_DIR = "/home/laoye/.openclaw/workspace/skills/agentcoin-mining"
PRIVATE_KEY = os.getenv("AGC_PRIVATE_KEY", "")

def log(msg):
    """静默日志（仅打印到stderr，不会触发消息）"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def send_telegram(message):
    """发送Telegram消息 - 使用openclaw message工具"""
    try:
        result = subprocess.run(
            ["openclaw", "message", "send", "--target", TELEGRAM_CHAT_ID, "--message", message],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        log(f"Telegram发送失败: {e}")
        return False

def get_submitted_ids():
    """获取已提交的题号列表"""
    if not os.path.exists(SUBMITTED_IDS_FILE):
        return set()
    try:
        with open(SUBMITTED_IDS_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        log(f"读取已提交记录失败: {e}")
        return set()

def add_submitted_id(problem_id):
    """添加已提交题号"""
    try:
        with open(SUBMITTED_IDS_FILE, 'a') as f:
            f.write(f"{problem_id}\n")
        log(f"已记录题号 #{problem_id}")
    except Exception as e:
        log(f"记录题号失败: {e}")

def fetch_problem():
    """获取当前题目"""
    try:
        # 获取挖矿状态
        status_resp = requests.get(f"{AGENTCOIN_API_BASE}/mining/status", timeout=10)
        status_data = status_resp.json()
        log(f"Status: {json.dumps(status_data, indent=2)[:200]}")
        
        # 获取当前题目
        timestamp = int(time.time())
        problem_resp = requests.get(
            f"{AGENTCOIN_API_BASE}/problem/current?t={timestamp}", 
            timeout=10
        )
        problem_data = problem_resp.json()
        log(f"Problem: {json.dumps(problem_data, indent=2)[:300]}")
        
        return status_data, problem_data
    except Exception as e:
        log(f"获取题目失败: {e}")
        return None, None

def solve_problem(problem_text):
    """
    通用问题求解器
    根据题目类型选择合适的解法
    """
    problem_lower = problem_text.lower()
    
    # 尝试解析数学表达式
    try:
        # 常见数学问题模式
        import re
        
        # 1. 简单的算术表达式
        # 查找类似 "What is 123 + 456?" 或 "Calculate 789 * 3"
        math_patterns = [
            r'what is\s+([\d\s\+\-\*\/\(\)]+)\??',
            r'calculate\s+([\d\s\+\-\*\/\(\)]+)',
            r'compute\s+([\d\s\+\-\*\/\(\)]+)',
            r'([\d\s\+\-\*\/\(\)]+)\s*=\s*\?',
        ]
        
        for pattern in math_patterns:
            match = re.search(pattern, problem_lower)
            if match:
                expr = match.group(1).strip()
                # 清理表达式
                expr = expr.replace(' ', '')
                if expr:
                    result = eval(expr)
                    if isinstance(result, float):
                        result = int(result) if result == int(result) else result
                    return str(int(result)) if isinstance(result, (int, float)) else str(result)
        
        # 2. 斐波那契数列
        if 'fibonacci' in problem_lower or 'fib(n)' in problem_lower:
            n_match = re.search(r'fib\w*\s*\(?\s*(\d+)\s*\)?', problem_lower)
            if n_match:
                n = int(n_match.group(1))
                return str(fibonacci(n))
        
        # 3. 质数相关
        if 'prime' in problem_lower:
            # 找第n个质数
            nth_match = re.search(r'(\d+)(?:st|nd|rd|th)?\s+prime', problem_lower)
            if nth_match:
                n = int(nth_match.group(1))
                return str(find_nth_prime(n))
            
            # 质数个数
            count_match = re.search(r'how many primes', problem_lower)
            if count_match:
                range_match = re.search(r'between\s+(\d+)\s+and\s+(\d+)', problem_lower)
                if range_match:
                    start, end = int(range_match.group(1)), int(range_match.group(2))
                    return str(count_primes(start, end))
        
        # 4. 阶乘
        if 'factorial' in problem_lower:
            fact_match = re.search(r'(\d+)!', problem_text)
            if fact_match:
                n = int(fact_match.group(1))
                return str(factorial(n))
        
        # 5. 数字序列/模式识别
        sequence_match = re.search(r'(\d+),\s*(\d+),\s*(\d+)', problem_text)
        if sequence_match:
            nums = [int(sequence_match.group(i)) for i in range(1, 4)]
            # 简单等差数列
            if nums[1] - nums[0] == nums[2] - nums[1]:
                diff = nums[1] - nums[0]
                next_num = nums[2] + diff
                return str(next_num)
        
        # 6. 最大公约数GCD
        if 'gcd' in problem_lower or 'greatest common divisor' in problem_lower:
            gcd_match = re.search(r'gcd\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', problem_lower)
            if gcd_match:
                a, b = int(gcd_match.group(1)), int(gcd_match.group(2))
                return str(gcd(a, b))
        
        # 7. 最小公倍数LCM
        if 'lcm' in problem_lower or 'least common multiple' in problem_lower:
            lcm_match = re.search(r'lcm\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', problem_lower)
            if lcm_match:
                a, b = int(lcm_match.group(1)), int(lcm_match.group(2))
                return str(lcm(a, b))
        
    except Exception as e:
        log(f"求解错误: {e}")
    
    return None

# 数学辅助函数
def fibonacci(n):
    """计算斐波那契数列第n项"""
    if n <= 0: return 0
    if n == 1: return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def is_prime(n):
    """判断是否为质数"""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0: return False
    return True

def find_nth_prime(n):
    """找第n个质数"""
    count = 0
    num = 1
    while count < n:
        num += 1
        if is_prime(num):
            count += 1
    return num

def count_primes(start, end):
    """计算区间内的质数个数"""
    return sum(1 for i in range(max(2, start), end + 1) if is_prime(i))

def factorial(n):
    """计算阶乘"""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def gcd(a, b):
    """最大公约数"""
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    """最小公倍数"""
    return (a * b) // gcd(a, b)

def submit_answer(problem_id, answer):
    """提交答案"""
    try:
        cmd = [
            "python3", "submit.py",
            str(problem_id),
            str(answer)
        ]
        
        env = os.environ.copy()
        env["AGC_PRIVATE_KEY"] = PRIVATE_KEY
        
        result = subprocess.run(
            cmd,
            cwd=SUBMIT_SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        log(f"提交输出: {result.stdout}")
        log(f"提交错误: {result.stderr}")
        
        # 解析结果
        output = result.stdout + result.stderr
        
        # 检查是否成功
        if result.returncode == 0 or "success" in output.lower() or "submitted" in output.lower():
            # 提取tx hash和gas
            import re
            tx_match = re.search(r'0x[a-fA-F0-9]{64}', output)
            tx = tx_match.group(0)[:10] + "..." if tx_match else "未知"
            
            gas_match = re.search(r'gas[:\s]+(\d+)', output, re.IGNORECASE)
            gas = gas_match.group(1) if gas_match else "未知"
            
            return True, tx, gas
        else:
            return False, None, output[:100]
            
    except subprocess.TimeoutExpired:
        return False, None, "提交超时"
    except Exception as e:
        return False, None, str(e)[:100]

def main():
    """主执行流程"""
    log("=== AGC解题执行器启动 ===")
    
    # 1. 获取题目
    status_data, problem_data = fetch_problem()
    
    if not problem_data:
        log("无法获取题目数据，退出")
        return
    
    # 2. 检查是否活跃
    is_active = problem_data.get("is_active", False)
    if not is_active:
        log("当前无活跃题目，静默退出")
        return
    
    # 3. 获取题目信息
    problem_id = str(problem_data.get("id", ""))
    problem_text = problem_data.get("problem", "")
    
    if not problem_id:
        log("无法获取题号，退出")
        return
    
    log(f"发现活跃题目 #{problem_id}: {problem_text[:100]}...")
    
    # 4. 检查是否已提交
    submitted_ids = get_submitted_ids()
    if problem_id in submitted_ids:
        log(f"题号 #{problem_id} 已提交过，跳过")
        return
    
    # 5. 求解
    answer = solve_problem(problem_text)
    if answer is None:
        error_msg = "无法求解该题目"
        log(error_msg)
        send_telegram(f"❌ AGC失败 | 题号#{problem_id} | 原因: {error_msg}")
        return
    
    log(f"求解成功，答案: {answer}")
    
    # 6. 提交
    success, tx_or_error, gas_or_detail = submit_answer(problem_id, answer)
    
    if success:
        # 记录已提交
        add_submitted_id(problem_id)
        # 发送成功消息
        send_telegram(f"✅ AGC成功 | 题号#{problem_id} | 答案{answer} | tx前缀{tx_or_error} | gas{gas_or_detail}")
        log(f"提交成功！")
    else:
        # 发送失败消息
        send_telegram(f"❌ AGC失败 | 题号#{problem_id} | 原因:{tx_or_error}")
        log(f"提交失败: {tx_or_error}")

if __name__ == "__main__":
    main()
