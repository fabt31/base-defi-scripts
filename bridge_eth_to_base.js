/**
 * Bridge ETH from Ethereum L1 to Base L2
 * Uses the official Base Bridge (Optimism Standard Bridge)
 */
const { ethers } = require("ethers");
require("dotenv").config();

// Official Base Bridge on Ethereum L1
const L1_STANDARD_BRIDGE = "0x3154Cf16ccdb4C6d922629664174b904d80F2C35";

const L1_BRIDGE_ABI = [
  {
    inputs: [
      { name: "_minGasLimit", type: "uint32" },
      { name: "_extraData", type: "bytes" },
    ],
    name: "bridgeETH",
    outputs: [],
    stateMutability: "payable",
    type: "function",
  },
];

async function bridgeETHtoBase(amountETH, minGasLimit = 200000) {
  const l1Provider = new ethers.providers.JsonRpcProvider(
    process.env.L1_RPC || "https://eth.llamarpc.com"
  );
  const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, l1Provider);
  console.log("Bridging from wallet:", wallet.address);

  const bridge = new ethers.Contract(L1_STANDARD_BRIDGE, L1_BRIDGE_ABI, wallet);
  const value = ethers.utils.parseEther(amountETH.toString());

  const l1Balance = await l1Provider.getBalance(wallet.address);
  console.log("L1 ETH balance:", ethers.utils.formatEther(l1Balance));
  console.log(`Bridging ${amountETH} ETH to Base...`);

  const tx = await bridge.bridgeETH(minGasLimit, "0x", { value });
  console.log("Bridge tx sent:", tx.hash);
  const receipt = await tx.wait();
  console.log("Bridge tx confirmed! Block:", receipt.blockNumber);
  console.log("ETH will arrive on Base in ~1-5 minutes.");
  console.log("Track on: https://bridge.base.org/transactions");
}

const amount = parseFloat(process.argv[2] || "0.01");
bridgeETHtoBase(amount).catch(console.error);
