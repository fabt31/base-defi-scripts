const { ethers } = require("ethers");
require("dotenv").config();

// Uniswap v3 SwapRouter02 on Base
const SWAP_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481";

// Token addresses on Base mainnet
const WETH = "0x4200000000000000000000000000000000000006";
const USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";

const ROUTER_ABI = [
  {
    inputs: [{
      components: [
        { name: "tokenIn", type: "address" },
        { name: "tokenOut", type: "address" },
        { name: "fee", type: "uint24" },
        { name: "recipient", type: "address" },
        { name: "amountIn", type: "uint256" },
        { name: "amountOutMinimum", type: "uint256" },
        { name: "sqrtPriceLimitX96", type: "uint160" },
      ],
      name: "params",
      type: "tuple",
    }],
    name: "exactInputSingle",
    outputs: [{ name: "amountOut", type: "uint256" }],
    stateMutability: "payable",
    type: "function",
  },
];

const ERC20_ABI = [
  "function approve(address spender, uint256 amount) returns (bool)",
  "function balanceOf(address) view returns (uint256)",
  "function decimals() view returns (uint8)",
];

async function swapUSDCtoWETH(amountUSDC) {
  const provider = new ethers.providers.JsonRpcProvider(
    process.env.BASE_RPC || "https://mainnet.base.org"
  );
  const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
  console.log("Swapping from:", wallet.address);

  const usdc = new ethers.Contract(USDC, ERC20_ABI, wallet);
  const router = new ethers.Contract(SWAP_ROUTER, ROUTER_ABI, wallet);

  const amountIn = ethers.utils.parseUnits(amountUSDC.toString(), 6);
  const balance = await usdc.balanceOf(wallet.address);
  console.log("USDC balance:", ethers.utils.formatUnits(balance, 6));

  // Approve router
  console.log("Approving USDC...");
  const approveTx = await usdc.approve(SWAP_ROUTER, amountIn);
  await approveTx.wait();
  console.log("Approved. Tx:", approveTx.hash);

  // Swap USDC -> WETH (fee tier: 0.05% = 500)
  const params = {
    tokenIn: USDC,
    tokenOut: WETH,
    fee: 500,
    recipient: wallet.address,
    amountIn,
    amountOutMinimum: 0,
    sqrtPriceLimitX96: 0,
  };

  console.log(`Swapping ${amountUSDC} USDC for WETH...`);
  const swapTx = await router.exactInputSingle(params);
  const receipt = await swapTx.wait();
  console.log("Swap successful! Tx:", receipt.transactionHash);
}

const amountUSDC = parseFloat(process.argv[2] || "10");
swapUSDCtoWETH(amountUSDC).catch(console.error);
