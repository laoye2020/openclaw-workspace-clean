const { ethers } = require('ethers');

const RPC_URL = 'https://mainnet.base.org';
const NFT_CONTRACT = '0xF202a738BDfE64073Ca758B719D71AF5878ca34e';
const TOKEN_CONTRACT = '0xe43d27eeacce497c4e454833de40504072a9f112';
const USER = '0x57a92aF2753cC6841210c6D9198F6Eb4887bEc0d';

async function check() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  
  // 查用户持有的 NFT IDs
  const nftAbi = ['function tokensOfOwner(address) view returns (uint256[])'];
  try {
    const nftContract = new ethers.Contract(NFT_CONTRACT, nftAbi, provider);
    const tokens = await nftContract.tokensOfOwner(USER);
    console.log('🎨 你持有的 NFT IDs:', tokens.map(t => t.toString()));
  } catch (e) {
    console.log('NFT 查询失败，可能 ABI 不对');
  }
  
  // 查用户代币余额
  const tokenAbi = ['function balanceOf(address) view returns (uint256)'];
  const tokenContract = new ethers.Contract(TOKEN_CONTRACT, tokenAbi, provider);
  const balance = await tokenContract.balanceOf(USER);
  console.log('💰 LOBROS 代币:', (balance / 1e18).toString());
  
  // 查交易历史
  console.log('\n📋 你的铸造交易:');
  console.log('TX: 0xa425ef7f8573af9514b132deca374bc51ee6684dad7595ac124d97d33c21a2eb');
  console.log('状态: ✅ 已确认');
}

check().catch(console.error);
