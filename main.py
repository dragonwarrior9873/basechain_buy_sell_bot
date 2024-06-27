from uniswap_universal_router_decoder import FunctionRecipient, RouterCodec
from web3 import Account, Web3
from web3.exceptions import InvalidAddress
from decimal import Decimal, getcontext
import time
from env import factory_v2_address, factory_v3_address, router_v2_address, weth_address,pair_address,usdc_address, permit2_address, rpc_endpoint_base, rpc_endpoint_eth, chain_id, private_key, ur_address, weth_address
from abi import  weth_abi, degen_abi, permit2_abi, router_v2_abi
import sys
import asyncio

w3base = Web3(Web3.HTTPProvider(rpc_endpoint_base))
w3eth = Web3(Web3.HTTPProvider(rpc_endpoint_eth))
account = Account.from_key(private_key)

minimal_pool_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "fee",
        "outputs": [{"internalType": "uint24", "name": "", "type": "uint24"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
        {
        "constant": True,
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            # other slot0 return values omitted for brevity
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "liquidity",
        "outputs": [{"internalType": "uint128", "name": "", "type": "uint128"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

factory_v3_abi = [
    {
        "inputs":[
            {"internalType":"address","name":"","type":"address"},
            {"internalType":"address","name":"","type":"address"},
            {"internalType":"uint24","name":"","type":"uint24"}
            ],
        "name":"getPool",
        "outputs":[{"internalType":"address","name":"","type":"address"}],
        "stateMutability":"view",
        "type":"function"
    }
]

factory_v2_abi = [
    {
        "constant":True,
        "inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],
        "name":"getPair",
        "outputs":[{"internalType":"address","name":"","type":"address"}],
        "payable":False,
        "stateMutability":"view",
        "type":"function"
    }
]

codec = RouterCodec()
uniswap_version = 1

def pool_address_get(token0, token1):
    global uniswap_version
    factory_v3_contract = w3base.eth.contract(address=factory_v3_address, abi=factory_v3_abi)
    factory_v2_contract = w3base.eth.contract(address=factory_v2_address, abi=factory_v2_abi)
    pair_address_v2 = factory_v2_contract.functions.getPair(token0, token1).call()
    if pair_address_v2 != "0x0000000000000000000000000000000000000000":
        uniswap_version = 2
        return pair_address_v2
    pair_address_v3 = factory_v3_contract.functions.getPool(token0, token1, 3000).call()
    if pair_address_v3 != "0x0000000000000000000000000000000000000000":
        uniswap_version = 3
        return pair_address_v3
    return None

def pool_address_sell_get(token0, token1):
    global uniswap_version
    factory_v3_contract = w3base.eth.contract(address=factory_v3_address, abi=factory_v3_abi)
    factory_v2_contract = w3base.eth.contract(address=factory_v2_address, abi=factory_v2_abi)
    pair_address_v2 = factory_v2_contract.functions.getPair(token0, token1).call()
    if pair_address_v2 != "0x0000000000000000000000000000000000000000":
        uniswap_version = 2
        return pair_address_v2
    pair_address_v3 = factory_v3_contract.functions.getPool(token0, token1, 3000).call()
    if pair_address_v3 != "0x0000000000000000000000000000000000000000":
        uniswap_version = 3
        return pair_address_v3
    return None

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

async def buy(args) -> None:
    if not args:
        text = "Please input command correctly. e.g: /buy 0x000000000000000 0.00001"
        print(text)
        return
    
    if args[2] is not None:
        if args[2].startswith("0x") is False:
            text = "Input Value Error. e.g : /buy 0x000000000000000 0.00001"
            print(text)
            return

    if args[3] is not None:
        if is_number(args[3]) is False:
            text = "Input Value Error. e.g : /buy 0x000000000000000 0.00001"
            print(text)
            return
        if is_number(args[3]) is True:
            text = args[3]

    if text is None:
       text = "No actions, invalid command"
       print(text)
       return
    
    token_address = Web3.to_checksum_address(args[2])
    pair_address = pool_address_get(weth_address, token_address)
    if pair_address is None:
        print("Pool Not Exist")
        return
    print("Buy start++++++++++")
    if uniswap_version == 3:
        try:
            token_contract = w3base.eth.contract(address=token_address, abi=degen_abi)
            # Example logic, adjust according to your asset names
            print(f"buy action called")
            # limit_buy_amount = 1 * 10**13
            limit_buy_amount = int(float(text) * 10**18)
            print(limit_buy_amount)
            min_amount_out = 365 * 10**10
            degen_balance_old = token_contract.functions.balanceOf(account.address).call()
        
            path = [weth_address, 3000 , token_address]
            codec = RouterCodec()

            encoded_input = (
                    codec
                    .encode
                    .chain()
                    .wrap_eth(FunctionRecipient.ROUTER, limit_buy_amount)
                    .v3_swap_exact_in(FunctionRecipient.SENDER, limit_buy_amount, min_amount_out, path, payer_is_sender=False)
                    .build(codec.get_default_deadline())
            )
            gas_price = w3base.to_wei(1, 'gwei')
            print(gas_price)
            trx_params = {
                    "from": account.address,
                    "to": ur_address,
                    "gas": 500_000,
                    "gasPrice": gas_price,
                    "chainId": chain_id,
                    "value": limit_buy_amount,
                    "nonce": w3base.eth.get_transaction_count(account.address),
                    "data": encoded_input,
            }

            raw_transaction = w3base.eth.account.sign_transaction(trx_params, account.key).rawTransaction
            trx_hash = w3base.eth.send_raw_transaction(raw_transaction)
                    
            result = w3base.eth.wait_for_transaction_receipt(trx_hash)
            if result['status'] == 0 :
                print("Uniswap v3 execution reverted")
                return
            degen_balance = token_contract.functions.balanceOf(account.address).call()
            trx_hash_hex = Web3.to_hex(trx_hash)  # Convert bytes to hexadecimal string
            text = f"Buy completed: {(degen_balance - degen_balance_old) / 10**18} Token received\n"
            text += f"You can check here. (https://basescan.org/tx/{trx_hash_hex})"
            print(text)
            print(w3base.eth.get_balance(account.address))
            print("buy completed")
        except (ValueError, InvalidAddress) as e:
            error_message = str(e)  # Convert the exception to a string to get the error message
            print(f"An error occurred: {error_message}")
            return
    
    if uniswap_version == 2:
        try:
            token_contract = w3base.eth.contract(address=token_address, abi=degen_abi)
            amount_in = int(float(text) * 10**18)
            token_allowance = token_contract.functions.allowance(account.address, router_v2_address).call()
            degen_balance_old = token_contract.functions.balanceOf(account.address).call()
            # if int(str(token_allowance), 10) < amount_in :
            #     # approve Permit2 to UNI
            #     router_allowance = 2**256 - 1  # max
            #     approval_tx = token_contract.functions.approve(router_v2_address, router_allowance).build_transaction({
            #         'from': account.address,
            #         'nonce': w3base.eth.get_transaction_count(account.address)
            #     })
            #     signed_approval_tx = w3base.eth.account.sign_transaction(approval_tx, account.key)
            #     tx_hash = w3base.eth.send_raw_transaction(signed_approval_tx.rawTransaction)
            #     w3base.eth.wait_for_transaction_receipt(tx_hash)
            
            buy_path = [weth_address, token_address]
            
            router_contract = w3base.eth.contract(address=router_v2_address, abi=router_v2_abi)
            gas_price = w3base.to_wei(1, 'gwei')
            buy_tx_params = {
                "nonce": w3base.eth.get_transaction_count(account.address),
                "from": account.address,
                "chainId": chain_id,
                "gas": 500_000,
                "gasPrice": gas_price,
                "value": amount_in,    
            }
            buy_tx = router_contract.functions.swapExactETHForTokens(
                    0, # min amount out
                    buy_path,
                    account.address,
                    int(time.time())+300 # deadline now + 180 sec
                ).build_transaction(buy_tx_params)

            signed_buy_tx = w3base.eth.account.sign_transaction(buy_tx, account.key)

            tx_hash = w3base.eth.send_raw_transaction(signed_buy_tx.rawTransaction)
            receipt = w3base.eth.wait_for_transaction_receipt(tx_hash)
            print(f"tx hash: {Web3.to_hex(tx_hash)}")
            if receipt['status'] == 0 :
                print("Uniswap v2 execution reverted")
                return
            
            degen_balance = token_contract.functions.balanceOf(account.address).call()
            trx_hash_hex = Web3.to_hex(tx_hash)  # Convert bytes to hexadecimal string
            text = f"Buy completed: {(degen_balance - degen_balance_old) / 10**18} Token received\n"
            text += f"You can check here. (https://basescan.org/tx/{trx_hash_hex})"
            print(text)
        except (ValueError, InvalidAddress) as e:
            error_message = str(e)  # Convert the exception to a string to get the error message
            print(f"An error occurred: {error_message}")
            return
                
async def sell(args) -> None:
    text = None
    global uniswap_version

    if not args:
        text = "Please input amount. e.g: /sell 0x000000000000000 0.1"
        print(text)
        return
    
    if args[2] is not None:
        if args[2].startswith("0x") is False:
            text = "Input Value Error. e.g : /sell 0x000000000000000 0.00001"
            print(text)
            return

    if args[3] is not None:
        if is_number(args[3]) is False:
            text = "Input Value Error. e.g : /sell 0x000000000000000 0.1"
            print(text)
            return
        if is_number(args[3]) is True:
            text = args[3]

    if text is None:
       text = "No actions, invalid command"
       print(text)
       return
    
    print(f"sell action called")
    token_address = Web3.to_checksum_address(args[2])
    pair_address = pool_address_sell_get(weth_address, token_address)
    if pair_address is None:
        print("Pool Not Exist")
        return
    token_contract = w3base.eth.contract(address=token_address, abi=degen_abi)
    token_balance_old = token_contract.functions.balanceOf(account.address).call()
    amount_in = int(float(text) * token_balance_old / 100)
    print("token_balance_old", token_balance_old)
    print("amount_in_percent", amount_in)
    token_allowance = token_contract.functions.allowance(account.address, permit2_address).call()
    # print(
    #             "Permit2 Degen allowance:",
    #             token_allowance,
    #     )
    # print(
    #             "Permit2 Degen allowance:",
    #             int(str(token_allowance), 10),
    #     )
    print("Sell Start++++++++++++")
    if int(str(token_allowance), 10) < amount_in :
        # approve Permit2 to UNI
        permit2_allowance = 2**256 - 1  # max
        print(f"approve")
        contract_function = token_contract.functions.approve(
                permit2_address,
                permit2_allowance
        )

        estimated_gas = contract_function.estimate_gas({
            "from": account.address,
            "value": 0,  # Adjust if your function sends value
        })

        # Add a margin to the estimated gas (e.g., 20% more)
        gas_limit_with_margin = int(estimated_gas * 1.2)
        print("gas_limit_with_margin = ",gas_limit_with_margin)
        gas_price = w3base.to_wei(1, 'gwei')
        trx_params = contract_function.build_transaction(
                {
                    "from": account.address,
                    "gas": 500_000,
                    "gasPrice": gas_price,
                    "chainId": chain_id,
                    "value": 0,
                    "nonce": w3base.eth.get_transaction_count(account.address),
                }
            )
        raw_transaction = w3base.eth.account.sign_transaction(trx_params, account.key).rawTransaction
        trx_hash = w3base.eth.send_raw_transaction(raw_transaction)
        w3base.eth.wait_for_transaction_receipt(trx_hash)
        print(
                "Permit2 Degen allowance:",
                token_contract.functions.allowance(account.address, permit2_address).call(),
        )

    if uniswap_version == 3:
        try:
            permit2_contract = w3base.eth.contract(address=permit2_address, abi=permit2_abi)

            p2_amount, p2_expiration, p2_nonce = permit2_contract.functions.allowance(
                    account.address,
                    token_address,
                    ur_address
            ).call()
        

            # permit message
            allowance_amount = 2**160 - 1  # max/infinite
            permit_data, signable_message = codec.create_permit2_signable_message(
                    token_address,
                    allowance_amount,
                    codec.get_default_expiration(),  # 30 days
                    p2_nonce,
                    ur_address,
                    codec.get_default_deadline(),  # 180 seconds
                    chain_id,
                )
            print("permit_data:", permit_data)
            print("signable_message:", signable_message)

            # Signing the message
            signed_message = account.sign_message(signable_message)
            # print("signed_message:", signed_message)

            # Building the Swap to sell UNI for USDT
            weth_contract = w3base.eth.contract(address=weth_address, abi=weth_abi)
            weth_balance_old = weth_contract.functions.balanceOf(account.address).call()

            min_amount_out = 415 * 10**6
            path = [token_address, 3000 ,weth_address]
            encoded_input = (
                    codec
                    .encode
                    .chain()
                    .permit2_permit(permit_data, signed_message)
                    .v3_swap_exact_in(
                            FunctionRecipient.SENDER,
                            amount_in,
                            min_amount_out,
                            path,
                            payer_is_sender=True,
                    )
                    .build(codec.get_default_deadline())
                )

            gas_price = w3base.to_wei(1, 'gwei')
            trx_params = {
                    "from": account.address,
                    "to": ur_address,
                    "gas": 500_000,
                    "gasPrice": gas_price,
                    "chainId": chain_id,
                    "value": 0,
                    "nonce": w3base.eth.get_transaction_count(account.address),
                    "data": encoded_input,
            }
            raw_transaction = w3base.eth.account.sign_transaction(trx_params, account.key).rawTransaction
            trx_hash = w3base.eth.send_raw_transaction(raw_transaction)
            print(f"Trx Hash: {trx_hash.hex()}")
            w3base.eth.wait_for_transaction_receipt(trx_hash)
            
            # Checking the balances
            degen_balance = token_contract.functions.balanceOf(account.address).call()
            print("Degen Balance:", degen_balance / 10**18, "DEGEN")

            weth_balance = weth_contract.functions.balanceOf(account.address).call()
            print("WETH Balance:", weth_balance / 10**18, "WETH")

            trx_hash_hex = Web3.to_hex(trx_hash)  # Convert bytes to hexadecimal string
            text = f"Sell completed: {(weth_balance - weth_balance_old) / 10**18} WETH received\n"
            text += f"You can check here. (https://basescan.org/tx/{trx_hash_hex})"
            print(text)

            # Checking the new Permit2 allowance
            p2_amount, p2_expiration, p2_nonce = permit2_contract.functions.allowance(
                    account.address,
                    token_address,
                    ur_address
            ).call()
        
            print("sell completed")
        except (ValueError, InvalidAddress) as e:
            error_message = str(e)  # Convert the exception to a string to get the error message
            print(f"An error occurred: {error_message}")
            return
    
    if uniswap_version == 2:
        try:
            token_contract = w3base.eth.contract(address=token_address, abi=degen_abi)
            token_allowance = token_contract.functions.allowance(account.address, router_v2_address).call()
            degen_balance_old = token_contract.functions.balanceOf(account.address).call()
            amount_in = int(float(text) * degen_balance_old / 100)
            print("degen balance", degen_balance_old)
            weth_contract = w3base.eth.contract(address=weth_address, abi=weth_abi)
            eth_balance_old = w3base.eth.get_balance(account.address)
            print("ether balance", eth_balance_old)

            if int(str(token_allowance), 10) < amount_in :
                gas_price = w3base.to_wei(1, 'gwei')
                router_allowance = 2**256 - 1  # max
                approve_tx = token_contract.functions.approve(router_v2_address, router_allowance).build_transaction({
                        "gas": 500_000,
                        "gasPrice": gas_price,
                        "nonce": w3base.eth.get_transaction_count(account.address),
                })    

                signed_approve_tx = w3base.eth.account.sign_transaction(approve_tx, account.key)

                tx_hash = w3base.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
                w3base.eth.wait_for_transaction_receipt(tx_hash)
            
            sell_path = [token_address, weth_address]
            
            router_contract = w3base.eth.contract(address=router_v2_address, abi=router_v2_abi)
            gas_price = w3base.to_wei(1, 'gwei')
            sell_tx_params = {
                "nonce": w3base.eth.get_transaction_count(account.address),
                "from": account.address,
                "chainId": chain_id,
                "gas": 500_000,
                "gasPrice": gas_price,
            }
            sell_tx = router_contract.functions.swapExactTokensForETH(
                    amount_in, # amount to sell
                    0, # min amount out
                    sell_path,
                    account.address,
                    int(time.time())+300 # deadline now + 180 sec
                ).build_transaction(sell_tx_params)
            signed_sell_tx = w3base.eth.account.sign_transaction(sell_tx, account.key)

            tx_hash = w3base.eth.send_raw_transaction(signed_sell_tx.rawTransaction)
            receipt = w3base.eth.wait_for_transaction_receipt(tx_hash)
            print(f"tx hash: {Web3.to_hex(tx_hash)}")
            if receipt['status'] == 0 :
                print("Uniswap v2 execution reverted")
                return
            
            degen_balance = token_contract.functions.balanceOf(account.address).call()
            eth_balance = w3base.eth.get_balance(account.address)
            trx_hash_hex = Web3.to_hex(tx_hash)  # Convert bytes to hexadecimal string
            text = f"Sell completed.\n"
            text += f"You can check here. (https://basescan.org/tx/{trx_hash_hex})"
            print(text)
        except (ValueError, InvalidAddress) as e:
            error_message = str(e)  # Convert the exception to a string to get the error message
            print(f"An error occurred: {error_message}")
            return
    # Example logic, adjust according to your asset names

if __name__ == "__main__":
    async def main():
        if sys.argv[1] == "buy":
            await buy(sys.argv)
        else:
            await sell(sys.argv)
    
    asyncio.run(main())