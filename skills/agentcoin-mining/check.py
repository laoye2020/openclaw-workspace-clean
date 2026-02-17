#!/usr/bin/env python3
"""AgentCoin Miner - Simplified version using only requests"""
import os
import sys
import json
import requests

API_BASE = "https://api.agentcoin.site"
RPC_URL = "https://mainnet.base.org"

# Derive wallet from private key using simple keccak
def get_wallet_from_key(key_hex):
    try:
        from eth_account import Account
        acc = Account.from_key(key_hex)
        return acc.address
    except:
        # Fallback: use web3
        import subprocess
        result = subprocess.run([
            'python3', '-c',
            f'from web3 import Web3; from eth_account import Account; acc = Account.from_key("{key_hex}"); print(acc.address)'
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None

def check_wallet_balance(wallet):
    """Check ETH and AGC balance using Base RPC"""
    headers = {"Content-Type": "application/json"}
    
    # ETH balance
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [wallet, "latest"],
        "id": 1
    }
    try:
        resp = requests.post(RPC_URL, json=payload, headers=headers, timeout=10)
        data = resp.json()
        if 'result' in data:
            eth_wei = int(data['result'], 16)
            eth = eth_wei / 1e18
            return eth
    except Exception as e:
        print(f"Balance check error: {e}")
    return None

def check_agent_status(wallet):
    """Check agent registration status"""
    try:
        resp = requests.get(f"{API_BASE}/api/agent/{wallet}/status", timeout=10)
        return resp.json()
    except Exception as e:
        print(f"Status check error: {e}")
        return None

def get_current_problem():
    """Get current active problem"""
    try:
        resp = requests.get(f"{API_BASE}/api/problem/current", timeout=10)
        return resp.json()
    except Exception as e:
        print(f"Problem fetch error: {e}")
        return None

if __name__ == "__main__":
    private_key = os.getenv("AGC_PRIVATE_KEY")
    if not private_key:
        print("Set AGC_PRIVATE_KEY env var")
        sys.exit(1)
    
    # Try to get wallet address
    try:
        from eth_account import Account
        acc = Account.from_key(private_key)
        wallet = acc.address
    except ImportError:
        print("eth_account not available, trying web3...")
        try:
            from web3 import Web3
            from eth_account import Account
            acc = Account.from_key(private_key)
            wallet = acc.address
        except ImportError:
            print("Need web3 or eth_account package")
            sys.exit(1)
    
    print(f"Wallet: {wallet}")
    print(f"\n{'='*50}")
    
    # Check ETH balance
    eth_balance = check_wallet_balance(wallet)
    if eth_balance is not None:
        print(f"ETH Balance: {eth_balance:.6f} ETH")
        if eth_balance < 0.001:
            print("⚠️  Low balance! Need ETH for gas.")
    
    # Check agent status
    status = check_agent_status(wallet)
    if status:
        print(f"\nAgent Status:")
        print(f"  Registered: {status.get('is_registered', False)}")
        print(f"  Agent ID: {status.get('agent_id', 'N/A')}")
        print(f"  Claimable AGC: {status.get('claimable_rewards_agc', 0)}")
        print(f"  Current Problem: {status.get('current_problem_id', 'N/A')}")
        print(f"  Has Submitted: {status.get('has_submitted_current', False)}")
    else:
        print("\nAgent not registered or API error")
    
    # Get current problem
    problem = get_current_problem()
    if problem:
        print(f"\nCurrent Problem:")
        print(f"  ID: {problem.get('problem_id')}")
        print(f"  Active: {problem.get('is_active')}")
        print(f"  Status: {problem.get('status')}")
        print(f"  Template: {problem.get('template_text', 'N/A')[:100]}...")
