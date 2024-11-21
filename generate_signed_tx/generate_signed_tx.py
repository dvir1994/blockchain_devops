# This script generated a signed EIP-1559 transaction to be broadcasted to an RPC endpoint
# Originally it was used to compare response times to Arbitrum sequencer w/o call data
# for example, sending a non existing method call vs actually sending a tx to be calculated

#  time curl https://arb1-sequencer.arbitrum.io/rpc \
#   -X POST \
#   -H "Content-Type: application/json" \
#   --data '{"jsonrpc":"2.0","method":"eth_sendRawTransaction","params":["0x02f8738.....b023c373"],"id":1}'

from web3 import Web3

# Connect to Arbitrum RPC
RPC_URL = "RPC_URL"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
FROM_ADDRESS = "0xYOUR_ADDRESS"
TO_ADDRESS = "0xTO_ADDRESS"
VALUE_IN_ETH_TO_SEND = 0.00001
PRIVATE_KEY = "XYZ"  # To convert mnemonic to private key (mnemonic_to_private_key.py)
CHAIN_ID = 421611
GAS = 201646  # Gas limit

nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(FROM_ADDRESS))
to_address = Web3.to_checksum_address(TO_ADDRESS)
value = w3.to_wei(VALUE_IN_ETH_TO_SEND, "ether")

# Fetch current base fee
latest_block = w3.eth.get_block("latest")
base_fee = latest_block["baseFeePerGas"]
# Set maxFeePerGas to double the baseFee (adjust if necessary)
max_fee_per_gas = base_fee * 2
max_priority_fee_per_gas = w3.to_wei(1, "gwei")  # Set a reasonable miner tip

# EIP-1559 Transaction dictionary
transaction = {
    "chainId": CHAIN_ID,
    "nonce": nonce,
    "to": to_address,
    "value": value,
    "gas": GAS,
    "maxFeePerGas": max_fee_per_gas,
    "maxPriorityFeePerGas": max_priority_fee_per_gas,
    "type": 2,  # EIP-1559 transaction type
}

# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)

# Get the raw transaction data
raw_txn = signed_txn.rawTransaction.hex()
print(f"Signed transaction: {raw_txn}")
