"""Swap tokens on Aerodrome Finance (Base L2)
Aerodrome is the native AMM/DEX on Base.
Docs: https://aerodrome.finance
"""
import os
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
from utils.web3_helpers import get_w3, get_account, approve_token

load_dotenv()

AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
WETH = "0x4200000000000000000000000000000000000006"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

ROUTER_ABI = [
    {
        "name": "swapExactTokensForTokens",
        "type": "function",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "routes", "type": "tuple[]",
             "components": [
                 {"name": "from", "type": "address"},
                 {"name": "to", "type": "address"},
                 {"name": "stable", "type": "bool"},
                 {"name": "factory", "type": "address"}
             ]},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}]
    }
]

DEFAULT_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"

def swap_usdc_to_weth(amount_usdc: float, slippage_bps: int = 50):
    """Swap USDC -> WETH via Aerodrome volatile pool.
    
    Args:
        amount_usdc: Amount of USDC to swap (human-readable)
        slippage_bps: Slippage tolerance in basis points (default 50 = 0.5%)
    """
    w3 = get_w3()
    account = get_account()

    amount_in = int(amount_usdc * 1e6)  # USDC has 6 decimals

    approve_token(w3, account, USDC, AERODROME_ROUTER, amount_in)

    router = w3.eth.contract(address=AERODROME_ROUTER, abi=ROUTER_ABI)

    routes = [{
        "from": USDC,
        "to": WETH,
        "stable": False,
        "factory": DEFAULT_FACTORY
    }]

    # Estimate output (simplified — in prod use getAmountsOut)
    amount_out_min = 0  # WARNING: set real slippage in production

    deadline = w3.eth.get_block("latest")["timestamp"] + 300

    tx = router.functions.swapExactTokensForTokens(
        amount_in,
        amount_out_min,
        routes,
        account.address,
        deadline
    ).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 300_000,
    })

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Swap USDC->WETH: {tx_hash.hex()}")
    print(f"Status: {'success' if receipt['status'] == 1 else 'failed'}")
    return tx_hash

if __name__ == "__main__":
    import sys
    amount = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
    print(f"Swapping {amount} USDC -> WETH on Aerodrome...")
    swap_usdc_to_weth(amount)
