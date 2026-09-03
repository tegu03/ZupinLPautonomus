"""Minimal canonical ABI definitions for Uniswap V4 on Robinhood Chain."""

V4_POSITION_MANAGER_ABI = [
    {"type": "function", "name": "poolManager", "stateMutability": "view", "inputs": [], "outputs": [{"type": "address"}]},
    {"type": "function", "name": "nextTokenId", "stateMutability": "view", "inputs": [], "outputs": [{"type": "uint256"}]},
    {"type": "function", "name": "positionInfo", "stateMutability": "view", "inputs": [{"name": "tokenId", "type": "uint256"}], "outputs": [{"type": "uint256"}]},
    {"type": "function", "name": "getPositionLiquidity", "stateMutability": "view", "inputs": [{"name": "tokenId", "type": "uint256"}], "outputs": [{"type": "uint128"}]},
    {"type": "function", "name": "getPoolAndPositionInfo", "stateMutability": "view", "inputs": [{"name": "tokenId", "type": "uint256"}], "outputs": [{"name": "poolKey", "type": "tuple", "components": [
        {"name": "currency0", "type": "address"}, {"name": "currency1", "type": "address"}, {"name": "fee", "type": "uint24"}, {"name": "tickSpacing", "type": "int24"}, {"name": "hooks", "type": "address"}
    ]}, {"name": "info", "type": "uint256"}]},
]

V4_STATE_VIEW_ABI = [
    {"type": "function", "name": "poolManager", "stateMutability": "view", "inputs": [], "outputs": [{"type": "address"}]},
    {"type": "function", "name": "getSlot0", "stateMutability": "view", "inputs": [{"name": "poolId", "type": "bytes32"}], "outputs": [{"type": "uint160"}, {"type": "int24"}, {"type": "uint24"}, {"type": "uint24"}]},
    {"type": "function", "name": "getLiquidity", "stateMutability": "view", "inputs": [{"name": "poolId", "type": "bytes32"}], "outputs": [{"type": "uint128"}]},
    {"type": "function", "name": "getFeeGrowthGlobals", "stateMutability": "view", "inputs": [{"name": "poolId", "type": "bytes32"}], "outputs": [{"type": "uint256"}, {"type": "uint256"}]},
    {"type": "function", "name": "getFeeGrowthInside", "stateMutability": "view", "inputs": [{"name": "poolId", "type": "bytes32"}, {"name": "tickLower", "type": "int24"}, {"name": "tickUpper", "type": "int24"}], "outputs": [{"type": "uint256"}, {"type": "uint256"}]},
]

V4_QUOTER_ABI = [
    {"type": "function", "name": "poolManager", "stateMutability": "view", "inputs": [], "outputs": [{"type": "address"}]},
]
