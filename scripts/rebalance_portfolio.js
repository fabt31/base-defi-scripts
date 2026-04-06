/**
 * Portfolio Rebalancer for Base L2
 * Reads current token balances and suggests/executes swaps
 * to hit target allocation percentages.
 */

const { ethers } = require("ethers");
const fs = require("fs");
require("dotenv").config();

const provider = new ethers.JsonRpcProvider(
  process.env.BASE_RPC || "https://mainnet.base.org"
);

const ERC20_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function symbol() view returns (string)"
];

// Target allocation (must sum to 100)
const TARGET_ALLOCATION = {
  "0x4200000000000000000000000000000000000006": { symbol: "WETH", targetPct: 50 },
  "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913": { symbol: "USDC", targetPct: 30 },
  "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb": { symbol: "DAI",  targetPct: 20 },
};

async function getUSDValue(tokenAddress, balance, decimals) {
  // Simplified: use hardcoded prices for demo
  // In production, read from Chainlink or an on-chain oracle
  const prices = {
    "0x4200000000000000000000000000000000000006": 3000,   // WETH
    "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913": 1.0,   // USDC
    "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb": 1.0,   // DAI
  };
  const price = prices[tokenAddress] || 0;
  return (Number(balance) / 10 ** decimals) * price;
}

async function getPortfolio(walletAddress) {
  const portfolio = [];
  let totalUSD = 0;

  for (const [address, info] of Object.entries(TARGET_ALLOCATION)) {
    const token = new ethers.Contract(address, ERC20_ABI, provider);
    const balance = await token.balanceOf(walletAddress);
    const decimals = await token.decimals();
    const usdValue = await getUSDValue(address, balance, decimals);
    totalUSD += usdValue;
    portfolio.push({ address, ...info, balance, decimals, usdValue });
  }

  return { portfolio, totalUSD };
}

async function suggestRebalance(walletAddress) {
  console.log("\n=== Portfolio Rebalancer (Base L2) ===\n");
  const { portfolio, totalUSD } = await getPortfolio(walletAddress);

  console.log("Current portfolio (total ~$" + totalUSD.toFixed(2) + "):\n");

  for (const token of portfolio) {
    const currentPct = totalUSD > 0 ? (token.usdValue / totalUSD * 100) : 0;
    const diff = currentPct - token.targetPct;
    const action = diff > 2 ? "SELL" : diff < -2 ? "BUY" : "OK";
    console.log(
      token.symbol.padEnd(6),
      ("$" + token.usdValue.toFixed(2)).padStart(10),
      (currentPct.toFixed(1) + "%").padStart(7),
      "-> target", token.targetPct + "%",
      "| " + action
    );
  }
  console.log("\nNote: Swaps not executed automatically. Review before trading.");
}

const wallet = process.env.WALLET_ADDRESS || "0x0000000000000000000000000000000000000000";
suggestRebalance(wallet).catch(console.error);
