"""
Web3 helper utilities for Base DeFi scripts.
"""
import os
from web3 import Web3
from web3.middleware import geth_poa_middleware


def get_w3(rpc_url: str = None) -> Web3:
    """Create and return a Web3 instance for Base network."""
    url = rpc_url or os.getenv("BASE_RPC", "https://mainnet.base.org")
    w3 = Web3(Web3.HTTPProvider(url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    assert w3.is_connected(), f"Failed to connect to {url}"
    return w3


def get_account(w3: Web3, private_key: str = None):
    """Return an account object from a private key."""
    key = private_key or os.getenv("PRIVATE_KEY")
    if not key:
        raise ValueError("PRIVATE_KEY not set")
    return w3.eth.account.from_key(key)


def approve_token(w3: Web3, account, token_address: str, spender: str, amount: int) -> str:
    """Approve an ERC20 token allowance. Returns tx hash."""
    abi = [
        {"inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
         "name": "approve", "outputs": [{"type": "bool"}],
         "stateMutability": "nonpayable", "type": "function"},
        {"inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}],
         "name": "allowance", "outputs": [{"type": "uint256"}],
         "stateMutability": "view", "type": "function"},
    ]
    contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
    current = contract.functions.allowance(account.address, spender).call()
    if current >= amount:
        return "already_approved"
    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.approve(
        Web3.to_checksum_address(spender), amount
    ).build_transaction({"from": account.address, "nonce": nonce, "gas": 100_000})
    signed = w3.eth.account.sign_transaction(tx, account.key)
    receipt = w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.rawTransaction))
    return receipt.transactionHash.hex()


def get_token_balance(w3: Web3, token_address: str, wallet: str) -> tuple:
    """Return (balance_raw, decimals, symbol) for an ERC20 token."""
    abi = [
        {"inputs": [{"name": "account", "type": "address"}], "name": "balanceOf",
         "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
        {"inputs": [], "name": "decimals", "outputs": [{"type": "uint8"}],
         "stateMutability": "view", "type": "function"},
        {"inputs": [], "name": "symbol", "outputs": [{"type": "string"}],
         "stateMutability": "view", "type": "function"},
    ]
    contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
    balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
    decimals = contract.functions.decimals().call()
    symbol = contract.functions.symbol().call()
    return balance, decimals, symbol


def format_token(amount: int, decimals: int) -> str:
    return f"{amount / 10**decimals:.6f}"
