import json
import requests
from os import getenv
from utils.send_slack import send_slack_wallet_funds_notification
from slack_sdk import WebClient
from accounts import eoa_accounts
from ratelimit import sleep_and_retry, limits

SLACK_BOT_TOKEN = getenv("SLACK_BOT_TOKEN")
SLACK_CLIENT = WebClient(token=SLACK_BOT_TOKEN)  # Slack client instance
SLACK_RATE_LIMIT_CALLS = 1
SLACK_RATE_LIMIT_PERIOD = 1
RPC_RATE_LIMIT_CALLS = 1
RPC_RATE_LIMIT_PERIOD = 1

networks_data = {
    "Fantom": {
        "rpc_endpoint": "https://rpc.ftm.tools/",
        "native_token_symbol": "FTM",
        "amount_of_wallets": 300,
        "chain_id": 0xFA,
        "low_funds_threshold": 0.2,  # amount in native token
    },
    "Base": {
        "rpc_endpoint": "https://mainnet.base.org",
        "native_token_symbol": "ETH",
        "amount_of_wallets": 21,
        "chain_id": 0x2105,
        "low_funds_threshold": 0.0003,  # amount in native token
    },
    "Avalanche": {
        "rpc_endpoint": "https://api.avax.network/ext/bc/C/rpc",
        "native_token_symbol": "AVAX",
        "amount_of_wallets": 71,
        "chain_id": 0xA86A,
        "low_funds_threshold": 0.03,  # amount in native token
    },
    "BSC": {
        "rpc_endpoint": "https://bsc-dataseed.nariox.org",
        "native_token_symbol": "BNB",
        "amount_of_wallets": 80,
        "chain_id": 0x38,
        "low_funds_threshold": 0.0017,  # amount in native token
    },
}


# Check balance of a single account on a specified network
@sleep_and_retry
@limits(calls=RPC_RATE_LIMIT_CALLS, period=RPC_RATE_LIMIT_PERIOD)
def get_native_token_balance(rpc_url, account_address):

    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [account_address, "latest"],
        "id": 1,
    }

    response = requests.post(rpc_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    # The balance is returned in Wei (the smallest unit of Ether), convert it to Ether
    balance_wei = int(result["result"], 16)
    balance_native = balance_wei / 10**18

    return balance_native


# Main monitoring function
def monitor_accounts():

    for network in networks_data:
        amount_of_wallets_in_network = networks_data[network]["amount_of_wallets"]
        wallets_to_scan = list(eoa_accounts.items())[:amount_of_wallets_in_network]

        for account_index, account_address in wallets_to_scan:
            # Iterate over each network

            rpc_endpoint = networks_data[network]["rpc_endpoint"]
            network_threshold = networks_data[network]["low_funds_threshold"]
            network_native_token_symbol = networks_data[network]["native_token_symbol"]

            # Check balance of account
            account_balance = get_native_token_balance(rpc_endpoint, account_address)

            # If balance is below threshold, send Slack alert
            if account_balance < network_threshold:
                send_slack_wallet_funds_notification(
                    SLACK_CLIENT,
                    network,
                    account_address,
                    account_index,
                    account_balance,
                    network_native_token_symbol,
                    network_threshold,
                )


if __name__ == "__main__":
    # Start the monitoring process
    monitor_accounts()
