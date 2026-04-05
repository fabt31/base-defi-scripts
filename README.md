# Base DeFi Scripts

Python and JavaScript scripts for interacting with DeFi protocols on Base L2.

## Protocols Covered

- **Aerodrome Finance** - Base's native DEX (AMM)
- **Aave v3** - Lending/borrowing on Base
- **Uniswap v3** - Concentrated liquidity swaps
- **Moonwell** - Lending protocol on Base
- **Extra Finance** - Leveraged yield farming

## Scripts

| Script | Protocol | Description |
|--------|----------|-------------|
| `aerodrome_swap.py` | Aerodrome | Swap tokens via Aerodrome router |
| `aave_supply.py` | Aave v3 | Supply collateral and borrow |
| `uniswap_v3_swap.js` | Uniswap v3 | Execute swaps with price limits |
| `check_positions.py` | All | Monitor all DeFi positions |

## Prerequisites

```bash
pip install web3 python-dotenv
npm install ethers dotenv
```

## Usage

```bash
cp .env.example .env
# Fill in your wallet private key and RPC URL
python aerodrome_swap.py
```

## Network

Base Mainnet — Chain ID: 8453 | RPC: https://mainnet.base.org

## Disclaimer

Use at your own risk. Always test on Base Sepolia testnet first.
