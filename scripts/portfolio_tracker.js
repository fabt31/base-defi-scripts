const { ethers } = require("ethers");
require("dotenv").config();
const tokens = require("../config/base_tokens.json");

const ERC20_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function symbol() view returns (string)",
];

async function trackPortfolio(address) {
  const provider = new ethers.providers.JsonRpcProvider(
    process.env.BASE_RPC || "https://mainnet.base.org"
  );
  const addr = ethers.utils.getAddress(address);
  console.log("Portfolio for:", addr);
  console.log("=".repeat(50));

  const ethBal = await provider.getBalance(addr);
  console.log("ETH:", ethers.utils.formatEther(ethBal));

  console.log("\nERC20 Tokens:");
  for (const [name, info] of Object.entries(tokens.tokens)) {
    if (info.isNative) continue;
    try {
      const token = new ethers.Contract(info.address, ERC20_ABI, provider);
      const bal = await token.balanceOf(addr);
      if (bal.gt(0)) {
        const formatted = ethers.utils.formatUnits(bal, info.decimals);
        console.log(`  ${name}: ${parseFloat(formatted).toFixed(4)}`);
      }
    } catch (e) {
      // skip
    }
  }
  console.log("=".repeat(50));
}

const address = process.argv[2] || process.env.WALLET_ADDRESS;
if (!address) {
  console.error("Usage: node scripts/portfolio_tracker.js <address>");
  process.exit(1);
}
trackPortfolio(address).catch(console.error);
