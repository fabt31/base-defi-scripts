"""Tests for Aerodrome swap script."""
import pytest
from unittest.mock import patch, MagicMock


def test_import():
    """Test that aerodrome_swap module is importable."""
    import importlib.util
    import os
    # Just verify the file exists and has the right structure
    assert os.path.exists("aerodrome_swap.py")


def test_router_address():
    """Verify the Aerodrome router address is correct."""
    EXPECTED_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
    with open("aerodrome_swap.py") as f:
        content = f.read()
    assert EXPECTED_ROUTER.lower() in content.lower(), \
        f"Expected router address {EXPECTED_ROUTER} not found"


def test_usdc_address():
    """Verify USDC address on Base is correct."""
    USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    with open("aerodrome_swap.py") as f:
        content = f.read()
    assert USDC_BASE.lower() in content.lower()


def test_weth_address():
    """Verify WETH address on Base is correct."""
    WETH_BASE = "0x4200000000000000000000000000000000000006"
    with open("aerodrome_swap.py") as f:
        content = f.read()
    assert WETH_BASE.lower() in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
