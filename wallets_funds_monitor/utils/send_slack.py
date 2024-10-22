from dotenv import load_dotenv
from slack_sdk.errors import SlackApiError
from ratelimit import sleep_and_retry, limits

load_dotenv()

BOT_USERNAME = "Wallet Funds Monitor 🤖"
BOT_ICON_EMOJI = ":bell:"
SLACK_CHANNEL = "#monitoring"
SLACK_RATE_LIMIT_CALLS = 1
SLACK_RATE_LIMIT_PERIOD = 1

TEMPLATE_TX_MESSAGE = """*🔔 Low wallet funds*
`Network`: {network_id}
`Account address`: {account_address} (index {account_index})
`Account balance`: {native_token_balance} {network_native_token_symbol} (< {network_threshold} {network_native_token_symbol})
"""


@sleep_and_retry
@limits(calls=SLACK_RATE_LIMIT_CALLS, period=SLACK_RATE_LIMIT_PERIOD)
def send_slack_wallet_funds_notification(
    slack_client,
    network,
    account_address,
    account_index,
    native_token_balance,
    network_native_token_symbol,
    network_threshold,
):
    try:

        slack_client.chat_postMessage(
            text=TEMPLATE_TX_MESSAGE.format(
                network_id=network,
                account_address=account_address,
                account_index=account_index,
                native_token_balance=native_token_balance,
                network_native_token_symbol=network_native_token_symbol,
                network_threshold=network_threshold,
            ),
            channel=SLACK_CHANNEL,
            username=BOT_USERNAME,
            icon_emoji=BOT_ICON_EMOJI,
        )
    except SlackApiError as e:
        print(e)
