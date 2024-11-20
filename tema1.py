from multiversx_sdk import Address, ProxyNetworkProvider, ContractQuery, Transaction, TransactionPayload, UserSigner
from pathlib import Path
import base64, json

# Define Macros
CONTRACT_ADDRESS = "erd1qqqqqqqqqqqqqpgqrqz7r8yl5dav2z0fgnn302l2w7xynygruvaq76m26j"
PROXY_URL = "https://devnet-gateway.multiversx.com"
provider = ProxyNetworkProvider(PROXY_URL)
contract_address = Address.from_bech32(CONTRACT_ADDRESS)
MY_NAME = "andrei_stefan.fotin"
MY_WALLET = "erd15lv2d4z4rm36kz6eu46uahf9lq9c7akmemtvf5smjhz83ep3kx5sqwqcjg"
PRIVATE_KEY_PATH = Path("/home/stefan/new_wallet.pem")

# Enums for Class, Rarity, and Power
CLASS_ENUM = [
    "Warrior", "Mage", "Rogue", "Priest", "Hunter",
    "Warlock", "Shaman", "Druid", "Paladin"
]
RARITY_ENUM = ["Common", "Rare", "Epic", "Legendary"]
POWER_ENUM = ["Low", "Medium", "High"]

def decode_object(data, offset, type):
    # Calculate length
    length = int.from_bytes(data[offset:offset + 4], byteorder="big")
    offset += 4
    # Get object value
    object = data[offset:offset + length]
    offset += length

    if type == "number":
        # If it's number (BigUInt)
        return int.from_bytes(object, byteorder="big"), offset
    elif type == "str":
        # If it's string
        return object.decode('utf-8', errors='ignore'), offset
    elif type == "attributes":
        object = object.hex()

        return {
            "class": int(object[0:2], 16),
            "rarity": int(object[2:4], 16),
            "power": int(object[4:6], 16),
        }, offset

def decode_esdt_token_data(data):
    offset = 0

    # Decode token_type (1 byte)
    token_type = data[offset]
    offset += 1

    # Decode amount (BigUint)
    amount, offset = decode_object(data, offset, "number")

    # Decode frozen (1 byte)
    frozen = bool(data[offset])
    offset += 1

    # Decode hash (ManagedBuffer)
    token_hash, offset = decode_object(data, offset, "str")

    # Decode name (ManagedBuffer)
    name, offset = decode_object(data, offset, "str")

    # Decode attributes (ManagedBuffer)
    attributes, offset = decode_object(data, offset, "attributes")

    # Decode creator (32 bytes)
    creator = data[offset:offset + 32]
    offset += 32

    # Decode royalties (BigUint)
    royalties, offset = decode_object(data, offset, "number")

    # Decode uris (ManagedVec<ManagedBuffer>)
    uri_count = int.from_bytes(data[offset:offset + 4], byteorder="big")
    offset += 4
    uris = []
    for _ in range(uri_count):
        uri, offset = decode_object(data, offset, "str")
        uris.append(uri)

    return {
        "token_type": token_type,
        "amount": amount,
        "frozen": frozen,
        "hash": token_hash,
        "name": name,
        "attributes": attributes,
        "creator": creator.hex(),
        "royalties": royalties,
        "uris": uris
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
            for idx, metadata_base64 in enumerate(result.return_data, start=1):
                nft = base64.b64decode(metadata_base64)
                nft_details = decode_esdt_token_data(nft)
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
        # Check if all properties match
        if (nft['attributes']['rarity'] == card_properties['rarity'] and
            nft['attributes']['class'] == card_properties['class'] and
            nft['attributes']['power'] == card_properties['power'] and
            nft['name'] == 'BPDA-TRADING-CARD'):
            # If all properties match, return the NFT and its attributes
            print("Found a matching NFT: ", nft)
            return nft
    
    print("No matching NFT found.")
    return None

def create_esdt_nft(nft_to_exchange):
    #try:
        # Initialize the provider and signer
        signer = UserSigner.from_pem_file(PRIVATE_KEY_PATH)

        # NFT details
        nft_collection_name = "MYNFTCOLL-123456"  # Your NFT collection identifier
        quantity = 1  # Number of NFTs to mint
        attributes = {
            "rarity": nft_to_exchange['attributes']['rarity'],
            "class": nft_to_exchange['attributes']['class'],
            "power": nft_to_exchange['attributes']['power'],
        }
        uri = "https://i.ytimg.com/vi/h4vmWLMoCKg/hqdefault.jpg"
        nft_name = MY_NAME

        # Build the ESDTNFTCreate transaction payload
        function_name = "ESDTNFTCreate"
        payload = (
            f"{function_name}@"
            f"{nft_collection_name.encode('utf-8').hex()}@"
            f"{quantity.to_bytes(8, 'big').hex()}@"
            f"{nft_name.encode('utf-8').hex()}@"
            f"{json.dumps(attributes).encode('utf-8').hex()}@"
            f"{uri.encode('utf-8').hex()}"
        )
        transaction_payload = TransactionPayload(payload)

        # Create the transaction
        sender_address = Address.from_bech32(MY_WALLET)
        transaction = Transaction(
            nonce=provider.get_account(sender_address).nonce,
            sender=sender_address,
            receiver=sender_address,
            value=0,
            gas_limit=6000000,  # Adjust gas limit if necessary
            data=transaction_payload,
            chain_id="D",  # "1" for Mainnet; "D" for Devnet
        )

        # Sign the transaction
        signer.sign(transaction)

        # Send the transaction
        tx_hash = provider.send_transaction(transaction)
        print(f"NFT created successfully! Transaction Hash: {tx_hash}")

    # except Exception as e:
    #     print(f"An error occurred while creating the NFT: {e}")

def exchange_nft(nft_to_exchange):
    try:
        # Create and execute a contract query
        query = ContractQuery(
            contract=contract_address,
            function="exchange_nft",
            encoded_arguments=[nft_to_exchange['nonce']]
        )
        result = provider.query_contract(query)

        if result.return_code == "ok":
            print(f"NFT-ul cu nonce-ul {nft_to_exchange} a fost schimbat cu succes!")
            return result.return_data
        else:
            print(f"Eroare: {result.return_message}")
        print(result.return_data)

    except Exception as e:
        print(f"An error occurred while querying the smart contract: {e}")

# Call the functions
card_properties = query_assigned_nft_properties()
available_nfts = query_smart_contract_data()
nft_to_exchange = find_first_matchy_nft(card_properties, available_nfts)
created_nft = create_esdt_nft(nft_to_exchange)
exchange_nft(nft_to_exchange)