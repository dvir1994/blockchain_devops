import json
from mnemonic import Mnemonic
from bip_utils import Bip44, Bip44Coins, Bip44Changes

# Your 12-word or 24-word seed phrase (mnemonic)
SEED_PHRASE = "test test test test test test test test test test test test"
OUTPUT_FILE = "/Users/dvir/projects/macabim/devops/scripts/misc/accounts.json"

# Number of accounts to generate
NUM_ACCOUNTS = 300


def generate_accounts_from_seed(seed_phrase, num_accounts):
    # Initialize the Mnemonic class
    mnemo = Mnemonic("english")

    # Generate the seed from the seed phrase
    seed_bytes = mnemo.to_seed(seed_phrase)

    # Create BIP44 master key for Ethereum
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)

    accounts = {}
    for i in range(num_accounts):
        # Derive account key using BIP44 standard derivation path for Ethereum
        bip44_acc = (
            bip44_mst.Purpose()
            .Coin()
            .Account(0)
            .Change(Bip44Changes.CHAIN_EXT)
            .AddressIndex(i)
        )

        # Get address
        eth_address = bip44_acc.PublicKey().ToAddress()

        # Store account information in the JSON format
        accounts[f"{i}"] = eth_address

    return accounts


# Generate accounts
accounts = generate_accounts_from_seed(SEED_PHRASE, NUM_ACCOUNTS)


# Save accounts to a JSON file
with open(OUTPUT_FILE, "w") as f:
    json.dump(accounts, f, indent=4)
