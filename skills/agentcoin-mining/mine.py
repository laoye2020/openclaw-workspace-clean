#!/usr/bin/env python3
"""AgentCoin Auto Miner - Continuous mining loop"""
import os
import sys
import time
import json
import requests
from web3 import Web3
from eth_account import Account

API_BASE = "https://api.agentcoin.site"
RPC_URL = os.getenv("AGC_RPC_URL", "https://mainnet.base.org")
PROBLEM_MANAGER = "0x7D563ae2881D2fC72f5f4c66334c079B4Cc051c6"
AGENT_REGISTRY = "0x5A899d52C9450a06808182FdB1D1e4e23AdFe04D"
REWARD_DISTRIBUTOR = "0xD85aCAC804c074d3c57A422d26bAfAF04Ed6b899"

PROBLEM_ABI = [
    {"inputs": [{"name": "problemId", "type": "uint256"}, {"name": "answer", "type": "bytes32"}], "name": "submitAnswer", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "problemId", "type": "uint256"}], "name": "getProblem", "outputs": [{"components": [{"name": "answerHash", "type": "bytes32"}, {"name": "answerDeadline", "type": "uint256"}, {"name": "revealDeadline", "type": "uint256"}, {"name": "status", "type": "uint8"}, {"name": "correctCount", "type": "uint256"}, {"name": "totalCorrectWeight", "type": "uint256"}, {"name": "winnerCount", "type": "uint256"}, {"name": "verifiedWinnerCount", "type": "uint256"}], "name": "", "type": "tuple"}], "stateMutability": "view", "type": "function"},
]

REGISTRY_ABI = [
    {"inputs": [{"name": "wallet", "type": "address"}], "name": "getAgentId", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
]

class AutoMiner:
    def __init__(self, private_key):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.account = Account.from_key(private_key)
        self.wallet = self.account.address
        self.agent_id = None
        self.stats = {"submitted": 0, "gas_spent": 0.0}
        
        self.problem_mgr = self.w3.eth.contract(address=PROBLEM_MANAGER, abi=PROBLEM_ABI)
        self.registry = self.w3.eth.contract(address=AGENT_REGISTRY, abi=REGISTRY_ABI)
        
    def get_agent_id(self):
        # Prefer API (faster/less RPC hang), fallback to chain call
        try:
            s = requests.get(f"{API_BASE}/api/agent/{self.wallet}/status", timeout=8).json()
            aid = s.get('agent_id')
            if aid:
                self.agent_id = int(aid)
                return self.agent_id
        except:
            pass
        try:
            agent_id = self.registry.functions.getAgentId(self.wallet).call()
            if agent_id > 0:
                self.agent_id = agent_id
                return agent_id
        except:
            pass
        return None
    
    def get_agent_status(self):
        try:
            resp = requests.get(f"{API_BASE}/api/agent/{self.wallet}/status", timeout=10)
            return resp.json()
        except:
            return None
    
    def get_current_problem(self):
        try:
            resp = requests.get(f"{API_BASE}/api/problem/current", timeout=10)
            return resp.json()
        except:
            return None
    
    def solve_problem(self, template_text, agent_id):
        """Solve math/logic problem"""
        import re
        
        N = agent_id
        personalized = template_text.replace("{AGENT_ID}", str(N))
        print(f"  Problem: {personalized[:150]}...")
        
        try:
            # Pattern 1: Sum of integers divisible by X or Y but not Z
            # "sum of all positive integers k ≤ N such that k is divisible by 3 or 5, but not divisible by 15"
            sum_pattern = re.search(r'sum of all positive integers k\s*[≤<=]\s*(\d+|N).*?divisible by (\d+) or (\d+).*?(?:not divisible by|not by)\s*(\d+)', personalized, re.IGNORECASE)
            if sum_pattern:
                limit_str = sum_pattern.group(1)
                limit = N if limit_str == 'N' or limit_str == str(N) else int(limit_str)
                div1 = int(sum_pattern.group(2))
                div2 = int(sum_pattern.group(3))
                exclude = int(sum_pattern.group(4))
                
                total = 0
                for k in range(1, limit + 1):
                    if (k % div1 == 0 or k % div2 == 0) and k % exclude != 0:
                        total += k
                
                # Check for modulo at the end
                # "Then, take the result modulo (N mod 100 + 1)"
                mod_pattern = re.search(r'result modulo\s*\(\s*N\s*mod\s*(\d+)\s*([+\-])\s*(\d+)\s*\)', personalized)
                if mod_pattern:
                    base = int(mod_pattern.group(1))
                    op = mod_pattern.group(2)
                    offset = int(mod_pattern.group(3))
                    mod_val = (N % base) + offset if op == '+' else (N % base) - offset
                    total = total % mod_val
                else:
                    mod_match = re.search(r'modulo\s+(\d+)', personalized)
                    if mod_match:
                        total = total % int(mod_match.group(1))
                
                return total
            
            # Pattern 2: Totient sum with XOR
            # "S = Σ_{k=1}^{N} φ(k) * (N mod k) ... A = (S mod 10007) XOR (N mod 256)"
            if ('φ(k)' in personalized or 'totient' in personalized.lower()) and 'XOR' in personalized:
                # precompute phi 1..N (linear-ish sieve)
                phi = list(range(N + 1))
                for i in range(2, N + 1):
                    if phi[i] == i:
                        for j in range(i, N + 1, i):
                            phi[j] -= phi[j] // i
                S = 0
                for k in range(1, N + 1):
                    S += phi[k] * (N % k)
                A = (S % 10007) ^ (N % 256)
                return int(A)

            # Pattern 3: Sum of divisors
            # "sum of all divisors of N"
            divisor_pattern = re.search(r'sum of all divisors of\s+(\d+|\{AGENT_ID\})', personalized)
            if divisor_pattern:
                val = N if "AGENT_ID" in divisor_pattern.group(1) else int(divisor_pattern.group(1))
                total = 0
                for i in range(1, int(val**0.5) + 1):
                    if val % i == 0:
                        total += i
                        if i != val // i:
                            total += val // i
                return total
            
            # Pattern 3: Fibonacci sequence
            fib_pattern = re.search(r'Fibonacci number F_(\d+)', personalized)
            if fib_pattern:
                n = int(fib_pattern.group(1))
                if n <= 0:
                    return 0
                elif n == 1 or n == 2:
                    return 1
                a, b = 1, 1
                for _ in range(n - 2):
                    a, b = b, a + b
                return b
            
            # Pattern 4: Factorial
            fact_pattern = re.search(r'(\d+)!', personalized)
            if fact_pattern:
                n = int(fact_pattern.group(1))
                result = 1
                for i in range(2, n + 1):
                    result *= i
                return result
            
            # Pattern 5: Sequence with recurrence
            if "a_{k+1}" in personalized and "a_k^2" in personalized:
                # Extract a_0
                a0_match = re.search(r'a_0\s*=\s*(\d+)\s*mod\s*(\d+)', personalized)
                if a0_match:
                    val = int(a0_match.group(1))
                    mod = int(a0_match.group(2))
                    a0 = val % mod
                    
                    # Find target term
                    target_match = re.search(r'value of a_(\d+)', personalized)
                    if target_match:
                        target = int(target_match.group(1))
                        
                        # Find sequence modulo
                        seq_mod_match = re.search(r'a_{k\+1}\s*=.*mod\s+(\d+)', personalized)
                        seq_mod = int(seq_mod_match.group(1)) if seq_mod_match else mod
                        
                        a = a0
                        for k in range(target):
                            a = (a * a + 1) % seq_mod
                        return a
            
            # Pattern 6: Simple modular arithmetic
            mod_match = re.search(r'(\d+)\s*mod\s*(\d+)', personalized)
            if mod_match:
                val = int(mod_match.group(1))
                mod = int(mod_match.group(2))
                return val % mod
            
            # Pattern 7: Simple arithmetic expression
            calc_match = re.search(r'Calculate the value of (.+?)(?:\.|$)', personalized)
            if calc_match:
                expr = calc_match.group(1).strip()
                # Replace N with agent_id if present
                expr = expr.replace("N", str(N))
                # Safe eval
                result = eval(expr, {"__builtins__": {}}, {})
                return int(result)
                
        except Exception as e:
            print(f"  Solve error: {e}")
        
        return None
    
    def submit_answer(self, problem_id, answer):
        """Submit answer on-chain"""
        answer_bytes = answer.to_bytes(32, 'big')
        
        tx = self.problem_mgr.functions.submitAnswer(problem_id, answer_bytes).build_transaction({
            'from': self.wallet,
            'nonce': self.w3.eth.get_transaction_count(self.wallet),
            'gas': 300000,
            'gasPrice': self.w3.to_wei('0.1', 'gwei'),
        })
        
        signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        gas_cost = self.w3.from_wei(receipt.gasUsed * self.w3.to_wei('0.1', 'gwei'), 'ether')
        self.stats["submitted"] += 1
        self.stats["gas_spent"] += float(gas_cost)
        
        return {
            'tx_hash': tx_hash.hex(),
            'gas_used': receipt.gasUsed,
            'gas_cost': float(gas_cost),
            'success': receipt.status == 1
        }
    
    def mine_once(self):
        """Mine one problem"""
        print(f"\n{'='*60}")
        print(f"[{time.strftime('%H:%M:%S')}] Mining...")
        
        # Get agent ID
        if not self.agent_id:
            self.get_agent_id()
        if not self.agent_id:
            print("❌ Agent not registered")
            return False
        
        print(f"  Agent ID: {self.agent_id}")
        
        # Get problem
        problem = self.get_current_problem()
        if not problem:
            print("  No problem available")
            return False
        
        problem_id = problem.get('problem_id')
        is_active = problem.get('is_active')
        template = problem.get('template_text', '')
        
        print(f"  Problem #{problem_id} | Active: {is_active}")
        
        if not is_active:
            print("  Problem not active, waiting...")
            return False
        
        # Check if already submitted
        status = self.get_agent_status()
        if status and status.get('has_submitted_current'):
            print("  Already submitted for this problem")
            return False
        
        # Solve
        answer = self.solve_problem(template, self.agent_id)
        if answer is None:
            print("  ❌ Could not solve")
            return False
        
        print(f"  Answer: {answer}")
        
        # Submit
        try:
            result = self.submit_answer(problem_id, answer)
            if result['success']:
                print(f"  ✅ Submitted! TX: {result['tx_hash'][:20]}...")
                print(f"  Gas: {result['gas_used']} | Cost: {result['gas_cost']:.8f} ETH")
                return True
            else:
                print(f"  ❌ Transaction failed")
                return False
        except Exception as e:
            print(f"  ❌ Submit error: {e}")
            return False
    
    def run_loop(self, interval=300):
        """Run continuous mining loop"""
        print(f"🚀 AgentCoin Auto Miner Started")
        print(f"Wallet: {self.wallet}")
        print(f"Checking registration...")
        
        agent_id = self.get_agent_id()
        if not agent_id:
            print("❌ Agent not registered! Run register first.")
            return
        
        print(f"✅ Agent ID: {agent_id}")
        print(f"Starting mining loop (every {interval}s)...\n")
        
        while True:
            try:
                self.mine_once()
                print(f"\nStats: Submitted {self.stats['submitted']} | Gas spent {self.stats['gas_spent']:.8f} ETH")
                print(f"Sleeping {interval}s...")
                time.sleep(interval)
            except KeyboardInterrupt:
                print(f"\n\nStopped. Final stats:")
                print(f"Submitted: {self.stats['submitted']}")
                print(f"Gas spent: {self.stats['gas_spent']:.8f} ETH")
                break
            except Exception as e:
                print(f"\nError: {e}")
                time.sleep(30)

if __name__ == "__main__":
    private_key = os.getenv("AGC_PRIVATE_KEY")
    if not private_key:
        print("Set AGC_PRIVATE_KEY")
        sys.exit(1)
    
    miner = AutoMiner(private_key)
    
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        miner.mine_once()
    else:
        miner.run_loop()
