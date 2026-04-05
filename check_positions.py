"""
Check DeFi Positions on Base Network
Displays balances and positions for a given wallet across multiple protocols.
"""
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC = os.getenv("BASE_RPC", "https://mainnet.base.org")
WALLET = os.getenv("WALLET_ADDRESS") or os.getenv("ADDRESS")

# Token addresses
TOKENS = {
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "DAI":  "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    "cbETH": "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22",
}

# Aave aToken addresses on Base
ATOKENS = {
    "aUSDC": "0x4e65fE4DbA92790696d040ac24Aa414708F5c0AB",
    "aWETH": "0xD4a0e0b9149BCee3C920d2E00b5dE09138fd8bb7",
}

ERC20_ABI = [
    {"inputs": [{"name": "account", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "decimals",
     "outputs": [{"type": "uint8"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "symbol",
     "outputs": [{"type": "string"}], "stateMutability": "view", "type": "function"},
]


def check_positions(wallet_address: str):
    w3 = Web3(Web3.HTTPProvider(RPC))
    addr = Web3.to_checksum_address(wallet_address)

    print(f"Checking positions for: {addr}\n")

    # Native ETH balance
    eth_balance = w3.eth.get_balance(addr)
    print(f"ETH (native): {w3.from_wei(eth_balance, 'ether'):.6f}")

    # ERC20 token balances
    print("\n--- Token Balances ---")
    for name, token_addr in TOKENS.items():
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI
        )
        balance = contract.functions.balanceOf(addr).call()
        decimals = contract.functions.decimals().call()
        print(f"{name}: {balance / 10**decimals:.6f}")

    # Aave aToken balances
    print("\n--- Aave Supplied ---")
    for name, atoken_addr in ATOKENS.items():
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(atoken_addr), abi=ERC20_ABI
        )
        balance = contract.functions.balanceOf(addr).call()
        decimals = contract.functions.decimals().call()
        print(f"{name}: {balance / 10**decimals:.6f}")


if __name__ == "__main__":
    import sys
    address = sys.argv[1] if len(sys.argv) > 1 else WALLET
    if not address:
        print("Usage: python check_positions.py <wallet_address>")
        print("Or set WALLET_ADDRESS in .env")
    else:
        check_positions(address)
