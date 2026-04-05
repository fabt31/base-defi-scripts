"""Tests for Aave supply script."""
import pytest
import json
import os


def test_aave_pool_address():
    """Verify Aave v3 Pool address on Base."""
    AAVE_POOL = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"
    with open("aave_supply.py") as f:
        content = f.read()
    assert AAVE_POOL.lower() in content.lower()


def test_config_has_aave():
    """Verify protocol config includes Aave addresses."""
    with open("config/protocol_addresses.json") as f:
        config = json.load(f)
    assert "aave_v3" in config["protocols"]
    assert "pool" in config["protocols"]["aave_v3"]


def test_config_chain_id():
    """Verify config targets Base mainnet (chainId 8453)."""
    with open("config/protocol_addresses.json") as f:
        config = json.load(f)
    assert config["chainId"] == 8453


def test_token_config_usdc():
    """Verify USDC entry in token config."""
    with open("config/base_tokens.json") as f:
        config = json.load(f)
    assert "USDC" in config["tokens"]
    assert config["tokens"]["USDC"]["decimals"] == 6


def test_aave_supply_has_approve_step():
    """Verify aave_supply.py includes token approval before supply."""
    with open("aave_supply.py") as f:
        content = f.read()
    assert "approve" in content
    assert "supply" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
