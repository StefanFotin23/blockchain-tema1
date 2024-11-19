from multiversx_sdk import Address, ProxyNetworkProvider, ContractQuery
import base64

CONTRACT_ADDRESS = "erd1qqqqqqqqqqqqqpgqrqz7r8yl5dav2z0fgnn302l2w7xynygruvaq76m26j"
PROXY_URL = "https://devnet-gateway.multiversx.com"

def decode_card_properties(card_base64):
    """
    Decode the card properties from base64 and interpret the hex-encoded values.
    """
    try:
        # Decode from base64
        card_bytes = base64.b64decode(card_base64)
        card_hex = card_bytes.hex()

        # Each byte represents one property: class, rarity, power
        class_idx = int(card_hex[0:2], 16)
        rarity_idx = int(card_hex[2:4], 16)
        power_idx = int(card_hex[4:6], 16)

        # Return as a dictionary
        return {
            "class": class_idx,
            "rarity": rarity_idx,
            "power": power_idx,
        }
    except Exception as e:
        print(f"Error decoding card properties: {e}")
        return None

def query_assigned_nft_properties():
    """
    Query the smart contract to get your assigned NFT card properties using multiversx_sdk.
    """
    provider = ProxyNetworkProvider(PROXY_URL)

    # Define the contract address
    contract_address = Address.from_bech32(CONTRACT_ADDRESS)

    try:
        # Create and execute a contract query
        query = ContractQuery(
            contract=contract_address,
            function="getYourNftCardProperties",
            encoded_arguments=[]  # No arguments for this function
        )
        result = provider.query_contract(query)

        # Check if there is return data
        if result.return_data:
            # Decode the base64 response
            decoded_card_properties = decode_card_properties(result.return_data[0])
            print("Assigned NFT Card Properties:", decoded_card_properties)
            return decoded_card_properties
        else:
            print("No data returned by the smart contract.")
    except Exception as e:
        print(f"An error occurred while querying the smart contract: {e}")

# Call the function
query_assigned_nft_properties()
