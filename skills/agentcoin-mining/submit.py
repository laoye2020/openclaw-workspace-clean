#!/usr/bin/env python3
import os,sys
from web3 import Web3
from eth_account import Account

RPC_URL=os.getenv('AGC_RPC_URL','https://mainnet.base.org')
PROBLEM_MANAGER='0x7D563ae2881D2fC72f5f4c66334c079B4Cc051c6'
ABI=[{"inputs":[{"name":"problemId","type":"uint256"},{"name":"answer","type":"bytes32"}],"name":"submitAnswer","outputs":[],"stateMutability":"nonpayable","type":"function"}]

pk=os.getenv('AGC_PRIVATE_KEY')
if not pk:
    print('need AGC_PRIVATE_KEY'); sys.exit(1)
if len(sys.argv)<3:
    print('usage: submit.py <problem_id> <answer_int>'); sys.exit(1)
pid=int(sys.argv[1]); ans=int(sys.argv[2])

w3=Web3(Web3.HTTPProvider(RPC_URL))
acct=Account.from_key(pk)
ct=w3.eth.contract(address=PROBLEM_MANAGER,abi=ABI)

ans_bytes=ans.to_bytes(32,'big',signed=False)
tx=ct.functions.submitAnswer(pid,ans_bytes).build_transaction({
    'from':acct.address,
    'nonce':w3.eth.get_transaction_count(acct.address),
    'gas':300000,
    'gasPrice':w3.to_wei('0.1','gwei')
})
signed=w3.eth.account.sign_transaction(tx,pk)
th=w3.eth.send_raw_transaction(signed.raw_transaction)
rc=w3.eth.wait_for_transaction_receipt(th,timeout=60)
print({'tx':th.hex(),'status':rc.status,'gasUsed':rc.gasUsed})
