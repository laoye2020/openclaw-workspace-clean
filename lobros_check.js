const { ethers } = require('ethers');

const RPC_URL = 'https://mainnet.base.org';
const CONTRACT = '0xe43d27eeacce497c4e454833de40504072a9f112';
const ABI = ['function totalSupply() view returns (uint256)', 'function balanceOf(address) view returns (uint256)'];

async function check() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const contract = new ethers.Contract(CONTRACT, ABI, provider);
  
  const totalSupply = await contract.totalSupply();
  const balance = await contract.balanceOf('0x57a92aF2753cC6841210c6D9198F6Eb4887bEc0d');
  const walletBalance = await provider.getBalance('0x57a92aF2753cC6841210c6D9198F6Eb4887bEc0d');
  
  console.log('📊 Lobros 铸造进度:', totalSupply.toString(), '/ 3,000');
  console.log('💰 你的 LOBROS 余额:', balance.toString());
  console.log('💵 钱包 ETH 余额:', ethers.formatEther(walletBalance), 'ETH');
}

check().catch(console.error);
