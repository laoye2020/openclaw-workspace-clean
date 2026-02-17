#!/usr/bin/env python3
"""AgentCoin Registration Helper"""
import os
import sys
import json
import requests
import time

API_BASE = "https://api.agentcoin.site"
RPC_URL = "https://mainnet.base.org"
REGISTRY_ADDRESS = "0x5A899d52C9450a06808182FdB1D1e4e23AdFe04D"

def get_wallet_from_key(key_hex):
    from eth_account import Account
    acc = Account.from_key(key_hex)
    return acc.address

def request_bind(wallet):
    """Step 1: Request verification code"""
    try:
        resp = requests.post(
            f"{API_BASE}/api/x/request-bind",
            json={"wallet": wallet},
            timeout=10
        )
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def verify_tweet(wallet, x_handle, code):
    """Step 3: Verify the tweet was posted"""
    try:
        resp = requests.post(
            f"{API_BASE}/api/x/verify",
            json={
                "wallet": wallet,
                "x_handle": x_handle,
                "verification_code": code
            },
            timeout=10
        )
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def register_on_chain(private_key, x_hash):
    """Step 4: Register agent on blockchain"""
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    account = w3.eth.account.from_key(private_key)
    
    # Simple ABI for registerAgent
    abi = [{"inputs": [{"name": "xAccountHash", "type": "bytes32"}], "name": "registerAgent", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"}]
    contract = w3.eth.contract(address=REGISTRY_ADDRESS, abi=abi)
    
    tx = contract.functions.registerAgent(x_hash).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.to_wei('0.1', 'gwei'),
    })
    
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    
    return {
        'tx_hash': tx_hash.hex(),
        'status': 'success' if receipt.status == 1 else 'failed',
        'gas_used': receipt.gasUsed
    }

if __name__ == "__main__":
    private_key = os.getenv("AGC_PRIVATE_KEY")
    if not private_key:
        print("Set AGC_PRIVATE_KEY")
        sys.exit(1)
    
    wallet = get_wallet_from_key(private_key)
    print(f"Wallet: {wallet}")
    print(f"\n{'='*60}")
    
    # Step 1: Get verification code
    print("Step 1: Requesting verification code...")
    result = request_bind(wallet)
    if not result:
        print("Failed to get verification code")
        sys.exit(1)
    
    code = result.get('verification_code')
    expires = result.get('expires_in', 300)
    print(f"✅ Verification code: {code}")
    print(f"⏰ Expires in: {expires} seconds")
    print(f"\n{'='*60}")
    print("Step 2: POST A TWEET with this exact text:")
    print(f"\nI want to register my AI Agent! @agentcoinsite\n\nCode: {code}")
    print(f"\n{'='*60}")
    print("After posting, tell me your X handle (without @)")
