"""
Moonwell Lending Script for Base Network
Supplies collateral and optionally borrows from Moonwell.
"""
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC = os.getenv("BASE_RPC", "https://mainnet.base.org")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Moonwell mToken addresses on Base
M_USDC = Web3.to_checksum_address("0xEdc817A28E8B93B03976FBd4a3dDBc9f7D176c22")
USDC = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

MTOKEN_ABI = [
    {"inputs": [{"name": "mintAmount", "type": "uint256"}],
     "name": "mint", "outputs": [{"type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}],
     "name": "balanceOfUnderlying", "outputs": [{"type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "exchangeRateCurrent",
     "outputs": [{"type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
]

ERC20_ABI = [
    {"inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
     "name": "approve", "outputs": [{"type": "bool"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}],
     "name": "balanceOf", "outputs": [{"type": "uint256"}],
     "stateMutability": "view", "type": "function"},
]


def supply_moonwell_usdc(amount_usdc: float):
    w3 = Web3(Web3.HTTPProvider(RPC))
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Supplying to Moonwell from: {account.address}")

    usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)
    mtoken = w3.eth.contract(address=M_USDC, abi=MTOKEN_ABI)

    amount = int(amount_usdc * 1_000_000)  # USDC 6 decimals
    bal = usdc.functions.balanceOf(account.address).call()
    print(f"USDC balance: {bal/1e6:.2f}")
    assert bal >= amount, "Insufficient USDC balance"

    nonce = w3.eth.get_transaction_count(account.address)
    tx = usdc.functions.approve(M_USDC, amount).build_transaction(
        {"from": account.address, "nonce": nonce, "gas": 100_000}
    )
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    receipt = w3.eth.wait_for_transaction_receipt(
        w3.eth.send_raw_transaction(signed.rawTransaction)
    )
    print(f"Approved. Tx: {receipt.transactionHash.hex()}")

    nonce += 1
    tx = mtoken.functions.mint(amount).build_transaction(
        {"from": account.address, "nonce": nonce, "gas": 300_000}
    )
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    receipt = w3.eth.wait_for_transaction_receipt(
        w3.eth.send_raw_transaction(signed.rawTransaction)
    )
    print(f"Supplied {amount_usdc} USDC to Moonwell. Tx: {receipt.transactionHash.hex()}")


if __name__ == "__main__":
    import sys
    amount = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
    supply_moonwell_usdc(amount)
