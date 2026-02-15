const { ethers } = require('ethers');

const PRIVATE_KEY = '0e51abaa111995a3c7b85f02776294710d70001c56ccc9ec360798055c678eba';
const RPC_URL = 'https://mainnet.base.org';

async function mintLobros() {
  console.log('🔐 初始化钱包...');
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  
  console.log('📍 钱包地址:', wallet.address);
  
  const balance = await provider.getBalance(wallet.address);
  console.log('💰 余额:', ethers.formatEther(balance), 'ETH');
  
  if (balance < ethers.parseEther('0.02')) {
    console.log('❌ 余额不足，需要至少 0.02 ETH');
    return;
  }
  
  console.log('\n📋 Step 1: 请求数学挑战...');
  const challengeRes = await fetch(
    `https://api.lobros.fun/api/challenge?walletAddress=${wallet.address}`
  );
  const { challengeId, challenge, expiresAt } = await challengeRes.json();
  console.log('🎯 挑战题目:', challenge);
  
  console.log('\n🧮 Step 2: 解题...');
  const answer = Function('"use strict"; return (' + challenge + ')')();
  console.log('✅ 答案:', answer);
  
  console.log('\n✍️ Step 3: 获取签名...');
  const mintRes = await fetch(`https://api.lobros.fun/api/mint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      walletAddress: wallet.address,
      challengeId,
      answer,
      quantity: 1,
      expiresAt
    })
  });
  const { mintData, error } = await mintRes.json();
  
  if (error) {
    console.log('❌ 签名失败:', error);
    return;
  }
  
  console.log('✅ 签名获取成功!');
  console.log('   Nonce:', mintData.nonce);
  console.log('   Expiry:', new Date(mintData.expiry * 1000).toLocaleString());
  
  console.log('\n🚀 Step 4: 发送铸造交易...');
  const mintContract = new ethers.Contract(
    mintData.contractAddress,
    ['function mint(uint256 quantity, bytes32 nonce, uint256 expiry, bytes signature) external payable'],
    wallet
  );
  
  const tx = await mintContract.mint(
    mintData.quantity,
    mintData.nonce,
    mintData.expiry,
    mintData.signature,
    { value: mintData.value }
  );
  
  console.log('📤 交易已发送:', tx.hash);
  console.log('⏳ 等待确认...');
  
  const receipt = await tx.wait();
  console.log('✅ 铸造成功!');
  console.log('📦 区块:', receipt.blockNumber);
  console.log('🔗 TX:', tx.hash);
}

mintLobros().catch(console.error);
