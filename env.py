from web3 import Web3
rpc_endpoint_base = "https://base.llamarpc.com"
rpc_endpoint_eth = "https://rpc.mevblocker.io"

# rpc_endpoint_base   = "https://base-mainnet.g.alchemy.com/v2/O8xbcrtK7haf0g99QW3HROwQMNYNIZli"
# rpc_endpoint_eth    = "https://eth-mainnet.g.alchemy.com/v2/5LdBRVqAuqPJXhOBxlzAsYBJ53YuryC0"

chain_id = 8453
limit_buy_amount = 1 * 10**13
private_key = "412ff0f159f30e449502561072f58dc24930c7c7d1058b977c8ade7300d278c5"

degen_address = Web3.to_checksum_address(
    "0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed")
ur_address = Web3.to_checksum_address(
    "0x198EF79F1F515F02dFE9e3115eD9fC07183f02fC")
weth_address = Web3.to_checksum_address(
    "0x4200000000000000000000000000000000000006")
pair_address = Web3.to_checksum_address(
    "0xc9034c3e7f58003e6ae0c8438e7c8f4598d5acaa")
usdc_address = Web3.to_checksum_address(
    "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")
permit2_address = Web3.to_checksum_address(
    "0x000000000022D473030F116dDEE9F6B43aC78BA3")
factory_v2_address = Web3.to_checksum_address(
    "0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6")
factory_v3_address = Web3.to_checksum_address(
    "0x33128a8fC17869897dcE68Ed026d694621f6FDfD")
router_v2_address = Web3.to_checksum_address(
    "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24")
