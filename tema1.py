from multiversx_sdk import Address, ProxyNetworkProvider, ContractQuery
import base64, struct

CONTRACT_ADDRESS = "erd1qqqqqqqqqqqqqpgqrqz7r8yl5dav2z0fgnn302l2w7xynygruvaq76m26j"
PROXY_URL = "https://devnet-gateway.multiversx.com"
provider = ProxyNetworkProvider(PROXY_URL)
contract_address = Address.from_bech32(CONTRACT_ADDRESS)

def parse_esdt_token_data(binary_data):
    offset = 0

    # Token Type (Assuming 1 byte for simplicity)
    token_type = struct.unpack_from('<B', binary_data, offset)[0]
    offset += 1
    print(f"Token Type: {token_type}")

    # Amount (BigUint, length-prefixed)
    amount_length = struct.unpack_from('<I', binary_data, offset)[0]  # 4 bytes for length
    offset += 4
    amount = int.from_bytes(binary_data[offset:offset + amount_length], 'little')
    offset += amount_length
    print(f"Amount: {amount}")

    # Frozen (Boolean, 1 byte)
    frozen = struct.unpack_from('<?', binary_data, offset)[0]
    offset += 1
    print(f"Frozen: {frozen}")

    # Hash (Length-prefixed binary data)
    hash_length = struct.unpack_from('<I', binary_data, offset)[0]
    offset += 4
    hash_data = binary_data[offset:offset + hash_length].hex()
    offset += hash_length
    print(f"Hash: {hash_data}")

    # Name (Length-prefixed string)
    name_length = struct.unpack_from('<I', binary_data, offset)[0]
    offset += 4
    name = binary_data[offset:offset + name_length].decode('utf-8')
    offset += name_length
    print(f"Name: {name}")

    # Attributes (Length-prefixed binary data)
    attr_length = struct.unpack_from('<I', binary_data, offset)[0]
    offset += 4
    attributes = binary_data[offset:offset + attr_length].hex()
    offset += attr_length
    print(f"Attributes: {attributes}")

    # Creator (Assuming 32 bytes for an address)
    creator = binary_data[offset:offset + 32].hex()
    offset += 32
    print(f"Creator: {creator}")

    # Royalties (BigUint, length-prefixed)
    royalties_length = struct.unpack_from('<I', binary_data, offset)[0]
    offset += 4
    royalties = int.from_bytes(binary_data[offset:offset + royalties_length], 'little')
    offset += royalties_length
    print(f"Royalties: {royalties}")

    # URIs (ManagedVec: Count-prefixed list of length-prefixed strings)
    uri_count = struct.unpack_from('<I', binary_data, offset)[0]
    offset += 4
    uris = []
    for _ in range(uri_count):
        uri_length = struct.unpack_from('<I', binary_data, offset)[0]
        offset += 4
        uri = binary_data[offset:offset + uri_length].decode('utf-8')
        offset += uri_length
        uris.append(uri)
    print(f"URIs: {uris}")

    return {
        "token_type": token_type,
        "amount": amount,
        "frozen": frozen,
        "hash": hash_data,
        "name": name,
        "attributes": attributes,
        "creator": creator,
        "royalties": royalties,
        "uris": uris,
    }

def decode_nft_metadata(metadata_base64):
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
            print(base64.b64decode(result.return_data[0]),"\n\n", base64.b64decode(result.return_data[1]))
            print('\n\n', parse_esdt_token_data(base64.b64decode(result.return_data[0])), '\n\n', parse_esdt_token_data(base64.b64decode(result.return_data[1])), '\n')
            for idx, metadata_base64 in enumerate(result.return_data, start=1):
                nft_details = decode_nft_metadata(metadata_base64)
                if nft_details:
                    # Add nonce and details to the NFT
                    nft_details["nonce"] = idx  # Nonce is the 1-based index
                    nfts.append(nft_details)

            return nfts
        else:
            print("No data returned by the smart contract.")
    except Exception as e:
        print(f"An error occurred while querying the smart contract: {e}")

def find_first_matchy_nft(card_properties, available_nfts):
    for nft in available_nfts:
        print(nft)
        # Check if all properties match
        if (nft['rarity'] == card_properties['rarity'] and
            nft['class'] == card_properties['class'] and
            nft['power'] == card_properties['power']):
            # If all properties match, return the NFT and its attributes
            print("Found a matching NFT: ${nft}")
            return nft
    
    print("No matching NFT found.")
    return None

def exchange_nft():
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
card_properties = query_assigned_nft_properties()
available_nfts = query_smart_contract_data()
print(available_nfts)
nft_to_exchange = find_first_matchy_nft(card_properties, available_nfts)
#print(nft_to_exchange)
#exchange_nft()