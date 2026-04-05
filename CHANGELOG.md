# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `scripts/rebalance.py` - Portfolio rebalancing script
- `scripts/auto_compound.py` - Auto-compound yield farming rewards
- `scripts/portfolio_tracker.js` - Track all positions in one view

## [1.2.0] - 2024-03-01

### Added
- `utils/gas_optimizer.py` - EIP-1559 gas estimation utilities
- `utils/web3_helpers.py` - Shared Web3 utility functions
- `config/base_tokens.json` - Token address registry for Base
- `config/protocol_addresses.json` - Protocol contract addresses

## [1.1.0] - 2024-02-15

### Added
- `bridge_eth_to_base.js` - ETH bridging via official Base Bridge
- `uniswap_v3_swap.js` - Uniswap v3 exact input single swap
- `check_positions.py` - Multi-protocol position checker
- `aave_supply.py` - Supply assets to Aave v3 on Base

## [1.0.0] - 2024-01-20

### Added
- `aerodrome_swap.py` - Swap tokens on Aerodrome Finance
- Initial project setup with README and structure
