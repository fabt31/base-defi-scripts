"""
Aerodrome Finance swap script for Base L2
Aerodrome is the native AMM/DEX on Base network
"""
from web3 import Web3
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Base Mainnet config
BASE_RPC = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Aerodrome Router address on Base
AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"

# Common token addresses on Base
TOKENS = {
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "USDbC": "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
    "AERO": "0x940181a94A35A4569E4529A3CDfB74e38FD98631",
    "cbETH": "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22",
}

ROUTER_ABI = json.loads("""[
  {
    "inputs": [
      {"internalType": "uint256","name": "amountIn","type": "uint256"},
      {"internalType": "uint256","name": "amountOutMin","type": "uint256"},
      {"internalType": "tuple[]","name": "routes","type": "tuple[]",
        "components": [
          {"name": "from","type": "address"},
          {"name": "to","type": "address"},
          {"name": "stable","type": "bool"},
          {"name": "factory","type": "address"}
        ]
      },
      {"internalType": "address","name": "to","type": "address"},
      {"internalType": "uint256","name": "deadline","type": "uint256"}
    ],
    "name": "swapExactTokensForTokens",
    "outputs": [{"internalType": "uint256[]","name": "amounts","type": "uint256[]"}],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]""")


def swap_usdc_to_weth(amount_usdc: float):
    """Swap USDC to WETH on Aerodrome"""
    w3 = Web3(Web3.HTTPProvider(BASE_RPC))
    account = w3.eth.account.from_key(PRIVATE_KEY)
    
    router = w3.eth.contract(address=AERODROME_ROUTER, abi=ROUTER_ABI)
    amount_in = int(amount_usdc * 1e6)  # USDC has 6 decimals
    
    route = [{
        "from": TOKENS["USDC"],
        "to": TOKENS["WETH"],
        "stable": False,
        "factory": "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"  # Aerodrome factory
    }]
    
    deadline = w3.eth.get_block("latest")["timestamp"] + 300  # 5 min
    
    tx = router.functions.swapExactTokensForTokens(
        amount_in,
        0,  # amountOutMin - set slippage in production!
        route,
        account.address,
        deadline
    ).build_transaction({
        "from": account.address,
        "gas": 200000,
        "gasPrice": w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(account.address),
    })
    
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Swap tx: https://basescan.org/tx/{tx_hash.hex()}")
    return tx_hash


if __name__ == "__main__":
    swap_usdc_to_weth(10.0)  # Swap 10 USDC -> WETH
