"""Parse and decode on-chain events from Base L2 transactions.

Useful for debugging or monitoring contract activity.
"""
import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC", "https://mainnet.base.org")))

ERC20_TRANSFER_TOPIC = Web3.keccak(text="Transfer(address,address,uint256)").hex()
ERC20_APPROVAL_TOPIC = Web3.keccak(text="Approval(address,address,uint256)").hex()

def decode_transfer_event(log):
    """Decode an ERC20 Transfer event log."""
    if log["topics"][0].hex() != ERC20_TRANSFER_TOPIC:
        return None
    from_addr = "0x" + log["topics"][1].hex()[-40:]
    to_addr   = "0x" + log["topics"][2].hex()[-40:]
    amount    = int(log["data"].hex(), 16)
    return {
        "event": "Transfer",
        "from": Web3.to_checksum_address(from_addr),
        "to":   Web3.to_checksum_address(to_addr),
        "amount": amount,
        "contract": log["address"],
        "tx_hash": log["transactionHash"].hex(),
        "block": log["blockNumber"],
    }

def get_token_transfers(token_address: str, from_block: int, to_block: int = "latest"):
    """Fetch all Transfer events for a token in a block range."""
    logs = w3.eth.get_logs({
        "address": Web3.to_checksum_address(token_address),
        "fromBlock": from_block,
        "toBlock": to_block,
        "topics": [ERC20_TRANSFER_TOPIC]
    })
    return [decode_transfer_event(log) for log in logs if decode_transfer_event(log)]

def get_tx_events(tx_hash: str):
    """Get all events emitted by a transaction."""
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    events = []
    for log in receipt["logs"]:
        if not log["topics"]:
            continue
        topic0 = log["topics"][0].hex()
        if topic0 == ERC20_TRANSFER_TOPIC:
            decoded = decode_transfer_event(log)
            if decoded:
                events.append(decoded)
        else:
            events.append({
                "event": "Unknown",
                "topic0": topic0,
                "contract": log["address"],
                "tx_hash": tx_hash,
            })
    return events

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python event_parser.py <tx_hash>")
        sys.exit(1)
    tx = sys.argv[1]
    print("Parsing events for tx:", tx)
    events = get_tx_events(tx)
    for e in events:
        print(json.dumps(e, indent=2))
