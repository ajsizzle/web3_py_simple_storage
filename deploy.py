from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    
# Compile Solidity

install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*" : {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to rinkeby
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/b004e95efbc349c78d76d29f7187c56a"))
chain_id = 4
my_address = "0xB45726805132aB016e649323AFfeCD0F9bBA434C"
private_key = os.getenv("PRIVATE_KEY")


# Create the contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get latest Txn
nonce = w3.eth.getTransactionCount(my_address)
# 1. Build a Txn
# 2. Sign a Txn
# 3. Send a Txn
txn = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
# Send this signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

# Working with the contract, you always need
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> simulate making the call and getting the return value
# Transact -> Actually make a state change

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("Updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId": chain_id, "from": my_address, "nonce": nonce + 1
})
signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Update successful!")
print(simple_storage.functions.retrieve().call())
