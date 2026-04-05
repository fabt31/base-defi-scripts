"""
Aave v3 Supply Script for Base Network
Supplies an ERC20 token to Aave v3 on Base to earn yield.
"""
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("BASE_RPC", "https://mainnet.base.org")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Aave v3 Pool on Base mainnet
AAVE_POOL = Web3.to_checksum_address("0xA238Dd80C259a72e81d7e4664a9801593F98d1c5")

# USDC on Base
USDC = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

POOL_ABI = [
    {
        "inputs": [
            {"name": "asset", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "onBehalfOf", "type": "address"},
            {"name": "referralCode", "type": "uint16"},
        ],
        "name": "supply",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

ERC20_ABI = [
    {"inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
     "name": "approve", "outputs": [{"type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}],
     "name": "balanceOf", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
]


def supply_usdc(amount_usdc: float):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    account = w3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    print(f"Supplying from: {address}")

    usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)
    pool = w3.eth.contract(address=AAVE_POOL, abi=POOL_ABI)

    # USDC has 6 decimals
    amount = int(amount_usdc * 1_000_000)
    balance = usdc.functions.balanceOf(address).call()
    print(f"USDC balance: {balance / 1e6:.2f}")
    assert balance >= amount, "Insufficient USDC balance"

    # Approve
    nonce = w3.eth.get_transaction_count(address)
    tx = usdc.functions.approve(AAVE_POOL, amount).build_transaction(
        {"from": address, "nonce": nonce, "gas": 100_000}
    )
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    receipt = w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.rawTransaction))
    print(f"Approved. Tx: {receipt.transactionHash.hex()}")

    # Supply
    nonce += 1
    tx = pool.functions.supply(USDC, amount, address, 0).build_transaction(
        {"from": address, "nonce": nonce, "gas": 300_000}
    )
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    receipt = w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.rawTransaction))
    print(f"Supplied {amount_usdc} USDC to Aave. Tx: {receipt.transactionHash.hex()}")


if __name__ == "__main__":
    import sys
    amount = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
    supply_usdc(amount)
