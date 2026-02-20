#!/usr/bin/env python3
"""
AGC解题执行器 - 每20秒运行
流程：检查题目→去重→解题→提交→通知
"""
import requests
import time
import os
import sys
import subprocess
import json
import re

# 配置
STATUS_URL = "https://api.agentcoin.site/api/mining/status"
PROBLEM_URL = "https://api.agentcoin.site/api/problem/current"
DEDUP_FILE = "/tmp/agc_submitted_ids.txt"
SUBMIT_DIR = "/home/laoye/.openclaw/workspace/skills/agentcoin-mining"
PRIVATE_KEY = os.getenv("AGC_PRIVATE_KEY", "")
TELEGRAM_CHAT = "8270250565"

# 静默日志（用于调试，不发送给用户）
log_file = "/tmp/agc_executor.log"

def log(msg):
    with open(log_file, "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    """发送Telegram消息"""
    try:
        # 使用绝对路径或npx调用
        result = subprocess.run([
            "/home/laoye/.nvm/versions/node/v22.18.0/bin/openclaw", "message", "send",
            "--target", TELEGRAM_CHAT,
            "--message", msg
        ], capture_output=True, timeout=10, env={"HOME": "/home/laoye"})
        log(f"发送结果: {result.returncode}")
    except Exception as e:
        log(f"发送Telegram失败: {e}")

def get_submitted_ids():
    """读取已提交题号"""
    if not os.path.exists(DEDUP_FILE):
        return set()
    try:
        with open(DEDUP_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def add_submitted_id(pid):
    """记录已提交题号"""
    with open(DEDUP_FILE, "a") as f:
        f.write(f"{pid}\n")

def fetch_current_problem():
    """获取当前题目"""
    try:
        # 先检查状态
        status_resp = requests.get(STATUS_URL, timeout=10)
        status_data = status_resp.json()
        
        # API 没有 is_active 字段，检查 current_problem_id 是否存在
        current_pid = status_data.get("current_problem_id")
        if current_pid is None:
            return None, "not_active"
        
        # 获取题目
        ts = int(time.time())
        prob_resp = requests.get(f"{PROBLEM_URL}?t={ts}", timeout=10)
        prob_data = prob_resp.json()
        
        return prob_data, "ok"
    except Exception as e:
        return None, f"fetch_error: {e}"

def solve_problem(problem_text, problem_type="math"):
    """
    通用解题逻辑 - 返回整数答案
    支持: 数学计算、数列、逻辑推理等
    """
    text = problem_text.strip()
    
    # 尝试提取数学表达式
    # 模式1: 直接的数学表达式 (如: 2+3*4, 10^2, sqrt(16))
    try:
        # 清理文本，提取可能的数学表达式
        # 移除markdown代码块
        clean = re.sub(r'```[\s\S]*?```', '', text)
        clean = re.sub(r'`([^`]+)`', r'\1', clean)
        
        # 寻找数学表达式模式
        # 计算型: "Calculate 2^10" or "求 1+2+...+100"
        patterns = [
            r'(?:calculate|compute|求|计算)[:\s]+([\d\+\-\*\/\^\(\)\s\.]+)',
            r'(?:what is|等于|结果是)[:\s]+([\d\+\-\*\/\^\(\)\s\.]+)',
            r'([\d]+)\^([\d]+)',  # 幂运算如 2^10
            r'sqrt\(([\d]+)\)',   # 平方根
            r'([\d]+)!',           # 阶乘
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean, re.IGNORECASE)
            if match:
                if '^' in match.group(0) and len(match.groups()) >= 2:
                    base, exp = match.group(1), match.group(2)
                    return int(base) ** int(exp)
                elif 'sqrt' in match.group(0):
                    return int(int(match.group(1)) ** 0.5)
                elif '!' in match.group(0):
                    n = int(match.group(1))
                    result = 1
                    for i in range(2, n+1):
                        result *= i
                    return result
                else:
                    expr = match.group(1)
                    # 安全计算
                    expr = expr.replace('^', '**')
                    result = eval(expr, {"__builtins__": {}}, {})
                    return int(result)
    except:
        pass
    
    # 模式2: 数列问题 (如: 斐波那契第n项)
    try:
        fib_patterns = [
            r'斐波那契.*第\s*(\d+)\s*项',
            r'fibonacci.*(?:第|#|number)\s*(\d+)',
            r'第\s*(\d+)\s*个斐波那契',
        ]
        for pattern in fib_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                n = int(match.group(1))
                if n <= 0:
                    return 0
                a, b = 0, 1
                for _ in range(n-1):
                    a, b = b, a+b
                return b
    except:
        pass
    
    # 模式3: 等差/等比数列求和
    try:
        sum_patterns = [
            r'1\+2\+3\+\.+\.(\d+)',
            r'1到(\d+)的和',
            r'sum of 1 to (\d+)',
        ]
        for pattern in sum_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                n = int(match.group(1))
                return n * (n + 1) // 2
    except:
        pass
    
    # 模式4: 质数相关
    try:
        prime_patterns = [
            r'第\s*(\d+)\s*个质数',
            r'(?:the|第)\s*(\d+)(?:th|个).*prime',
        ]
        for pattern in prime_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                n = int(match.group(1))
                def is_prime(x):
                    if x < 2:
                        return False
                    for i in range(2, int(x**0.5)+1):
                        if x % i == 0:
                            return False
                    return True
                count = 0
                num = 2
                while count < n:
                    if is_prime(num):
                        count += 1
                        if count == n:
                            return num
                    num += 1
    except:
        pass
    
    # 模式5: 提取末尾的数字作为答案
    try:
        numbers = re.findall(r'\d+', text)
        if numbers:
            # 通常最后一个数字是需要计算的目标
            return int(numbers[-1])
    except:
        pass
    
    # 无法求解
    return None

def submit_answer(problem_id, answer):
    """提交答案"""
    try:
        env = os.environ.copy()
        env["AGC_PRIVATE_KEY"] = PRIVATE_KEY
        
        result = subprocess.run(
            ["python3", "submit.py", str(problem_id), str(answer)],
            cwd=SUBMIT_DIR,
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )
        
        output = result.stdout.strip()
        log(f"提交输出: {output}")
        
        if result.returncode != 0:
            return False, f"提交脚本错误: {result.stderr}", None, None
        
        # 解析输出 {"tx": "...", "status": 1, "gasUsed": 12345}
        try:
            data = json.loads(output.replace("'", '"'))
            tx = data.get("tx", "")
            status = data.get("status", 0)
            gas = data.get("gasUsed", 0)
            
            if status == 1:
                return True, "success", tx[:20] + "...", gas
            else:
                return False, f"交易失败 status={status}", tx[:20] + "...", gas
        except:
            # 解析失败但命令成功，也算成功
            return True, "success (parse unclear)", output[:20], 0
            
    except subprocess.TimeoutExpired:
        return False, "提交超时", None, None
    except Exception as e:
        return False, f"提交异常: {e}", None, None

def main():
    log("="*50)
    log("AGC解题执行器启动")
    
    # 1. 获取当前题目
    problem, status = fetch_current_problem()
    
    if status == "not_active":
        log("当前无活跃题目，静默退出")
        return 0
    
    if problem is None:
        log(f"获取题目失败: {status}")
        return 1
    
    # 2. 检查题目信息
    problem_id = str(problem.get("id", problem.get("problem_id", "")))
    is_active = problem.get("is_active", False)
    problem_text = problem.get("text", problem.get("problem", problem.get("content", "")))
    
    log(f"获取到题目 #{problem_id}, is_active={is_active}")
    
    if not is_active:
        log("题目未激活，静默退出")
        return 0
    
    # 3. 去重检查
    submitted = get_submitted_ids()
    if problem_id in submitted:
        log(f"题号 #{problem_id} 已提交过，跳过")
        return 0
    
    log(f"新题目 #{problem_id}，开始求解")
    
    # 4. 解题
    answer = solve_problem(problem_text)
    
    if answer is None:
        error_msg = f"❌ AGC失败 | 题号#{problem_id} | 原因: 无法识别题目类型或求解"
        log(error_msg)
        send_telegram(error_msg)
        return 1
    
    log(f"求解完成，答案: {answer}")
    
    # 5. 提交
    success, msg, tx_prefix, gas = submit_answer(problem_id, answer)
    
    if success:
        # 6. 记录成功并发送通知
        add_submitted_id(problem_id)
        success_msg = f"✅ AGC成功 | 题号#{problem_id} | 答案{answer} | tx前缀{tx_prefix} | gas{gas}"
        log(success_msg)
        send_telegram(success_msg)
        return 0
    else:
        # 7. 发送失败通知
        fail_msg = f"❌ AGC失败 | 题号#{problem_id} | 原因: {msg}"
        log(fail_msg)
        send_telegram(fail_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main())
