from multiversx_sdk import Address, ProxyNetworkProvider, ContractQuery
import base64

CONTRACT_ADDRESS = "erd1qqqqqqqqqqqqqpgqrqz7r8yl5dav2z0fgnn302l2w7xynygruvaq76m26j"
PROXY_URL = "https://devnet-gateway.multiversx.com"
provider = ProxyNetworkProvider(PROXY_URL)
contract_address = Address.from_bech32(CONTRACT_ADDRESS)

def decode_nft_metadata(metadata_base64):
    """
    Decode NFT metadata from Base64 and parse the hex-encoded values.
    Each NFT has token ID, rarity, class, and power.
    """
    try:
        # Decode metadata from Base64
        metadata_bytes = base64.b64decode(metadata_base64)
        metadata_hex = metadata_bytes.hex()

        # Parse properties
        token_id = metadata_hex[:8]  # Assume first 4 bytes represent token ID
        rarity = int(metadata_hex[8:10], 16)  # Next byte is rarity
        class_idx = int(metadata_hex[10:12], 16)  # Next byte is class
        power = int(metadata_hex[12:14], 16)  # Next byte is power

        return {
            "token_id": token_id,
            "rarity": rarity,
            "class": class_idx,
            "power": power
        }
    except Exception as e:
        print(f"Error decoding NFT metadata: {e}")
        return None

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

def query_smart_contract_data():
    try:
        # Create and execute a contract query
        query = ContractQuery(
            contract=contract_address,
            function="nftSupply",
            encoded_arguments=[]  # No arguments for this function
        )
        result = provider.query_contract(query)

        # Check if there is return data
        if result.return_data:
            nfts = []
            for idx, metadata_base64 in enumerate(result.return_data, start=1):
                nft_details = decode_nft_metadata(metadata_base64)
                if nft_details:
                    # Add nonce and details to the NFT
                    nft_details["nonce"] = idx  # Nonce is the 1-based index
                    nfts.append(nft_details)

            print("NFTs fetched from the smart contract:", nfts)
            return nfts
        else:
            print("No data returned by the smart contract.")
    except Exception as e:
        print(f"An error occurred while querying the smart contract: {e}")

# Call the functions
query_assigned_nft_properties()
query_smart_contract_data()