"""Canonical ABI definitions for Uniswap V3 reads."""

V3_FACTORY_ABI = [
    {"type": "function", "name": "getPool", "stateMutability": "view", "inputs": [{"type": "address"}, {"type": "address"}, {"type": "uint24"}], "outputs": [{"type": "address"}]},
]

V3_POSITION_MANAGER_ABI = [
    {"type": "function", "name": "factory", "stateMutability": "view", "inputs": [], "outputs": [{"type": "address"}]},
]

V3_POOL_ABI = [
    {"type": "function", "name": "factory", "stateMutability": "view", "inputs": [], "outputs": [{"type": "address"}]},
    {"type": "function", "name": "token0", "stateMutability": "view", "inputs": [], "outputs": [{"type": "address"}]},
    {"type": "function", "name": "token1", "stateMutability": "view", "inputs": [], "outputs": [{"type": "address"}]},
    {"type": "function", "name": "fee", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint24"}]},
    {"type": "function", "name": "tickSpacing", "stateMutability": "view", "inputs": [], "outputs": [{"type": "int24"}]},
    {"type": "function", "name": "slot0", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint160"}, {"type": "int24"}, {"type": "uint16"}, {"type": "uint16"}, {"type": "uint16"}, {"type": "uint8"}, {"type": "bool"}]},
    {"type": "function", "name": "feeGrowthGlobal0X128", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint256"}]},
    {"type": "function", "name": "feeGrowthGlobal1X128", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint256"}]},
    {"type": "function", "name": "liquidity", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint128"}]},
]
