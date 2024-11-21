from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes


def mnemonic_to_private_key(mnemonic):
    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # Derive private key using BIP44 standard (for Ethereum)
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    bip44_acc = (
        bip44_mst.Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
    )

    # Get private key in hex format prefixed with '0x'
    return "0x" + bip44_acc.PrivateKey().Raw().ToHex()


# Example usage
mnemonic = "X Y Z"
private_key = mnemonic_to_private_key(mnemonic)
print("Private Key:", private_key)
