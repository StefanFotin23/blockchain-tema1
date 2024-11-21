import time
from pathlib import Path
from multiversx_sdk import ProxyNetworkProvider, UserSigner, Address, Transaction, TransactionPayload

# Initialize network provider
provider = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")
PEM_PATH = Path("/home/stefan/new_wallet.pem")
WALLET_ADDRESS = "erd15lv2d4z4rm36kz6eu46uahf9lq9c7akmemtvf5smjhz83ep3kx5sqwqcjg"

signer = UserSigner.from_pem_file(PEM_PATH)
account_address = Address.from_bech32(WALLET_ADDRESS)

# NFT details
nft_name = "BPDA-TRADING-CARD"
nft_ticker = "MYNFT"
class_id = 0
rarity_id = 1
power_id = 0
royalties = 10000

# Function to create the serialized data for signing
def serialize_for_signing(transaction):
    sender = transaction.sender.bech32()
    receiver = transaction.receiver.bech32()
    nonce = str(transaction.nonce)
    value = str(transaction.value)
    gas_price = str(transaction.gas_price)
    gas_limit = str(transaction.gas_limit)
    data = transaction.data.decode() if transaction.data else ""
    chain_id = transaction.chain_id

    parts = [
        sender,
        receiver,
        value,
        nonce,
        gas_price,
        gas_limit,
        data,
        chain_id,
    ]

    return "|".join(parts).encode()

# Main function to mint an NFT
def mint_nft():
    # Get account nonce
    account_info = provider.get_account(account_address)
    nonce = account_info.nonce

    # Create transaction data
    transaction_data = f"ESDTNFTCreate@{nft_ticker}@{1:02x}@{nft_name}@{class_id:02x}{rarity_id:02x}{power_id:02x}@{royalties}"
    
    # Convert data to bytes
    transaction_payload = transaction_data.encode()

    # Create and serialize the transaction
    transaction = Transaction(
        nonce=nonce,
        sender=account_address.bech32(),  # Convert Address to string
        receiver=account_address.bech32(),  # Convert Address to string
        value=0,
        gas_limit=500000,
        data=transaction_payload,
        chain_id="D",
    )

    # Serialize the transaction and sign it
    transaction_serialized = serialize_for_signing(transaction)
    transaction.signature = signer.sign(transaction_serialized)

    # Send the transaction
    transaction_response = provider.send_transaction(transaction)
    print(f"Transaction response: {transaction_response}")

# Run the main function
if __name__ == "__main__":
    mint_nft()
