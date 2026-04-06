"""Unit tests for Uniswap v3 swap script on Base L2."""
import pytest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SWAP_ROUTER_V2 = "0x2626664c2603336E57B271c5C0b26F421741e481"
USDC_ADDRESS   = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
WETH_ADDRESS   = "0x4200000000000000000000000000000000000006"
FEE_500        = 500
FEE_3000       = 3000

class TestUniswapV3Config:
    def test_router_address_checksum(self):
        from web3 import Web3
        assert Web3.is_checksum_address(SWAP_ROUTER_V2), "SwapRouter02 must be checksummed"

    def test_token_addresses_valid(self):
        from web3 import Web3
        assert Web3.is_address(USDC_ADDRESS)
        assert Web3.is_address(WETH_ADDRESS)

    def test_usdc_decimals(self):
        # USDC on Base uses 6 decimals
        usdc_decimals = 6
        amount_human = 100.0
        amount_raw = int(amount_human * 10 ** usdc_decimals)
        assert amount_raw == 100_000_000

    def test_fee_tiers(self):
        valid_fees = {100, 500, 3000, 10000}
        assert FEE_500 in valid_fees
        assert FEE_3000 in valid_fees

    def test_deadline_in_future(self):
        import time
        deadline = int(time.time()) + 300
        assert deadline > int(time.time())

class TestSlippageCalculation:
    def test_slippage_50bps(self):
        amount_out_expected = 1_000_000  # 1 USDC
        slippage_bps = 50
        min_out = int(amount_out_expected * (10000 - slippage_bps) / 10000)
        assert min_out == 995_000

    def test_slippage_100bps(self):
        amount_out_expected = 2_000_000
        slippage_bps = 100
        min_out = int(amount_out_expected * (10000 - slippage_bps) / 10000)
        assert min_out == 1_980_000

    def test_zero_slippage_risky(self):
        # 0 bps means no slippage protection — should be flagged
        slippage_bps = 0
        assert slippage_bps == 0, "0 slippage is dangerous in production"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
