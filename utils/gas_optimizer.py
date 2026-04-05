"""Gas optimization utilities for Base network transactions."""
import os
from web3 import Web3

BASE_RPC = os.getenv("BASE_RPC", "https://mainnet.base.org")

def get_base_fee(w3=None):
    """Get the current base fee in wei from the latest block."""
    if w3 is None:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
    block = w3.eth.get_block("latest")
    return block.get("baseFeePerGas", 0)

def get_priority_fee(w3=None):
    """Get estimated max priority fee per gas."""
    if w3 is None:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
    try:
        return w3.eth.max_priority_fee
    except Exception:
        return Web3.to_wei(0.001, "gwei")

def get_eip1559_fees(multiplier=1.2):
    """Returns EIP-1559 fee params: maxFeePerGas and maxPriorityFeePerGas."""
    w3 = Web3(Web3.HTTPProvider(BASE_RPC))
    base_fee = get_base_fee(w3)
    priority_fee = get_priority_fee(w3)
    max_fee = int(base_fee * multiplier) + priority_fee
    return {
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": priority_fee,
        "baseFeeGwei": base_fee / 1e9,
        "priorityFeeGwei": priority_fee / 1e9,
        "maxFeeGwei": max_fee / 1e9,
    }

def estimate_tx_cost_usd(gas_limit, eth_price_usd=3000.0):
    """Estimate transaction cost in USD."""
    fees = get_eip1559_fees()
    cost_wei = gas_limit * fees["maxFeePerGas"]
    cost_eth = cost_wei / 1e18
    return cost_eth * eth_price_usd

def print_gas_report(gas_limit=200_000):
    fees = get_eip1559_fees()
    print(f"Base Fee:     {fees['baseFeeGwei']:.4f} gwei")
    print(f"Priority Fee: {fees['priorityFeeGwei']:.4f} gwei")
    print(f"Max Fee:      {fees['maxFeeGwei']:.4f} gwei")
    cost_usd = estimate_tx_cost_usd(gas_limit)
    print(f"Estimated tx cost ({gas_limit} gas): ${cost_usd:.4f}")

if __name__ == "__main__":
    print_gas_report()
