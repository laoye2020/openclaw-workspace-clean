const { ethers } = require('ethers');

const RPC_URL = 'https://mainnet.base.org';
const NFT_CONTRACT = '0xF202a738BDfE64073Ca758B719D71AF5878ca34e';
const TOKEN_CONTRACT = '0xe43d27eeacce497c4e454833de40504072a9f112';
const USER = '0x57a92aF2753cC6841210c6D9198F6Eb4887bEc0d';

async function check() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  
  // 查 NFT 铸造数量
  const nftAbi = ['function _tokenIds() view returns (uint256)'];
  const nftContract = new ethers.Contract(NFT_CONTRACT, nftAbi, provider);
  const tokenIds = await nftContract._tokenIds();
  
  // 查用户代币余额
  const tokenAbi = ['function balanceOf(address) view returns (uint256)'];
  const tokenContract = new ethers.Contract(TOKEN_CONTRACT, tokenAbi, provider);
  const balance = await tokenContract.balanceOf(USER);
  
  console.log('🎯 已铸造 NFT 数量:', tokenIds.toString(), '/ 3,000');
  console.log('💰 你的 LOBROS 代币:', (balance / 1e18).toString());
}

check().catch(console.error);
