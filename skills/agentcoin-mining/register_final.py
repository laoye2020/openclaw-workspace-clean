#!/usr/bin/env python3
"""Complete AgentCoin Registration - Fixed"""
import os
import sys
import requests
from web3 import Web3
from eth_account import Account

API_BASE = "https://api.agentcoin.site"
RPC_URL = "https://mainnet.base.org"
REGISTRY_ADDRESS = "0x5A899d52C9450a06808182FdB1D1e4e23AdFe04D"

def get_x_hash(x_handle):
    """Calculate xAccountHash from X handle - returns bytes32"""
    w3 = Web3()
    return w3.keccak(text=x_handle.lower())

def verify_tweet(wallet, x_handle, code):
    try:
        resp = requests.post(
            f"{API_BASE}/api/x/verify",
            json={"wallet": wallet, "x_handle": x_handle, "verification_code": code},
            timeout=10
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def register_on_chain(private_key, x_hash):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    account = Account.from_key(private_key)
    
    abi = [{"inputs": [{"name": "xAccountHash", "type": "bytes32"}], "name": "registerAgent", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"}]
    contract = w3.eth.contract(address=REGISTRY_ADDRESS, abi=abi)
    
    tx = contract.functions.registerAgent(x_hash).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.to_wei('0.1', 'gwei'),
    })
    
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    
    return {'tx_hash': tx_hash.hex(), 'status': 'success' if receipt.status == 1 else 'failed', 'gas_used': receipt.gasUsed}

if __name__ == "__main__":
    private_key = os.getenv("AGC_PRIVATE_KEY")
    x_handle = os.getenv("X_HANDLE")
    code = os.getenv("CODE")
    
    if not all([private_key, x_handle, code]):
        print("Need AGC_PRIVATE_KEY, X_HANDLE, CODE")
        sys.exit(1)
    
    wallet = Account.from_key(private_key).address
    print(f"Wallet: {wallet}")
    print(f"X Handle: @{x_handle}")
    
    # Step 1: Verify
    print(f"\nStep 1: Verifying tweet...")
    result = verify_tweet(wallet, x_handle, code)
    print(f"Result: {result}")
    
    if not result.get('success'):
        print(f"❌ Verification failed")
        sys.exit(1)
    
    print("✅ Tweet verified!")
    
    # Step 2: Calculate xAccountHash
    x_hash = get_x_hash(x_handle)
    print(f"\nxAccountHash: {x_hash}")
    
    # Step 3: Register
    print(f"\nStep 2: Registering on-chain...")
    reg_result = register_on_chain(private_key, x_hash)
    
    if reg_result['status'] == 'success':
        print(f"✅ Registration successful!")
        print(f"TX: {reg_result['tx_hash']}")
        print(f"Gas used: {reg_result['gas_used']}")
    else:
        print(f"❌ Registration failed")
        print(f"TX: {reg_result['tx_hash']}")
