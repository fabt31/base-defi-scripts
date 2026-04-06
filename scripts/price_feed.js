/**
 * Price Feed Reader for Base L2
 * Reads Chainlink price feeds on Base mainnet.
 */

const { ethers } = require("ethers");
require("dotenv").config();

const provider = new ethers.JsonRpcProvider(
  process.env.BASE_RPC || "https://mainnet.base.org"
);

// Chainlink Price Feeds on Base Mainnet
const PRICE_FEEDS = {
  "ETH/USD":  "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70",
  "BTC/USD":  "0xCCADC697c55bbB68dc5bCdf8d3CBe83CdD4E071E",
  "USDC/USD": "0x7e860098F58bBFC8648a4311b374B1D669a2bc9b",
  "cbETH/ETH":"0x806b4Ac04501c29769051e42783cF04dCE41440b",
};

const AGGREGATOR_ABI = [
  "function latestRoundData() view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)",
  "function decimals() view returns (uint8)"
];

async function getPrice(feedName, feedAddress) {
  const feed = new ethers.Contract(feedAddress, AGGREGATOR_ABI, provider);
  const [, answer, , updatedAt] = await feed.latestRoundData();
  const decimals = await feed.decimals();
  const price = Number(answer) / 10 ** decimals;
  const age = Math.floor(Date.now() / 1000) - Number(updatedAt);
  return { feedName, price, ageSeconds: age };
}

async function getAllPrices() {
  console.log("\n=== Base L2 Chainlink Price Feeds ===\n");
  const results = await Promise.all(
    Object.entries(PRICE_FEEDS).map(([name, addr]) => getPrice(name, addr))
  );
  for (const { feedName, price, ageSeconds } of results) {
    console.log(
      feedName.padEnd(12),
      ("$" + price.toFixed(4)).padStart(14),
      "  (updated", ageSeconds, "s ago)"
    );
  }
}

getAllPrices().catch(console.error);
