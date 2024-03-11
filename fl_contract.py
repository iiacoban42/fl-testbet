"""Run with ganache-cli -m "pistol kiwi shrug future ozone ostrich match remove crucial oblige cream critic" --account_keys_path keys.json --accounts 55 --block-time 5 --gasPrice 100000000000"""
from web3 import Web3

GANACHE_URL = "http://127.0.0.1:8545"
CHAIN_ID = 1337

def deploy_contract(web3, model, num_rounds, server_account, private_key):
    # Load the compiled contract ABI and bytecode
    with open("contracts/abi/FL_sol_FL.abi", "r") as file:
        contract_abi = file.read()

    with open("contracts/abi/FL_sol_FL.bin", "r") as file:
        contract_bytecode = file.read()

    # Deploy the contract
    contract = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    # Get the number of latest transaction
    nonce = web3.eth.get_transaction_count(server_account)
    # build transaction
    transaction = contract.constructor(model, num_rounds).build_transaction(
        {
            "chainId": CHAIN_ID,
            "from": server_account,
            "nonce": nonce,
        }
    )
    # Sign the transaction
    sign_transaction = web3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("Deploying Contract!")
    # Send the transaction
    transaction_hash = web3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    # Wait for the transaction to be mined, and get the transaction receipt
    transaction_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")
    return contract, transaction_receipt.contractAddress


def set_weight(web3, contract, server_account, private_key, client_address, weight):
    # Get the number of latest transaction
    nonce = web3.eth.get_transaction_count(server_account)
    # Send a transaction to set value1
    t = contract.functions.storeWeights(weight).build_transaction(
        {
            "chainId": CHAIN_ID,
            "from": server_account,
            "to": client_address,
            "nonce": nonce,
        }
    )
    sign_transaction = web3.eth.account.sign_transaction(t, private_key=private_key)
    t_hash = web3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    t_receipt = web3.eth.wait_for_transaction_receipt(t_hash)

    # print(f"weights set successfully: {t_receipt}")



def set_aggregated_model(web3, contract, server_account, private_key, client_address, aggregated_model, accuracy, loss):

    nonce = web3.eth.get_transaction_count(server_account)
    client_address = web3.to_checksum_address(client_address)
    # Send another transaction to set value2
    t = contract.functions.storeAggregatedModel(aggregated_model, accuracy, loss).build_transaction(
        {
            "chainId": CHAIN_ID,
            "from": server_account,
            "to": client_address,
            "nonce": nonce,
        }
    )

    sign_transaction = web3.eth.account.sign_transaction(t, private_key=private_key)
    t_hash = web3.eth.send_raw_transaction(sign_transaction.rawTransaction)

    t_receipt = web3.eth.wait_for_transaction_receipt(t_hash)
    # print(f"aggregate model set successfully: {t_receipt}")

    # Client payout
    amount_to_transfer = web3.to_wei(1, "ether")
    t = web3.eth.send_transaction({
        "from": server_account,
        "to": client_address,
        "value": amount_to_transfer,
    })
    t_receipt = web3.eth.wait_for_transaction_receipt(t)
    # print(f"client payout successful: {t_receipt}")



def test():
    web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    server = "0x3dfee283e6fc51f8996efca126ae76571ba5906d"
    sk = "0x5eaac1a6910aa9a992cc63cbd90569bc72567a0f0e172d52ae24eee1efc5325e"
    client = "0x2ee1ac154435f542ecec55c5b0367650d8a5343b"
    number_of_rounds = 3
    model = "model"
    server = web3.to_checksum_address(server)
    client = web3.to_checksum_address(client)
    contract, contract_address = deploy_contract(web3, model, number_of_rounds, server, sk)
    print(f"Contract deployed at address: {contract_address}")
    for r in range(number_of_rounds):
        set_weight(web3, contract, server, sk, client, "w"+str(r))
        set_aggregated_model(web3, contract, server, sk, client, "w"+str(r), 90, 10)
        print(f"Round {r} completed")

# test()
