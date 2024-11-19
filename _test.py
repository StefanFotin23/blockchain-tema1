import struct
from typing import List

def decode_biguint(data, offset, is_length_prefixed=True):
    """Decode a BigUint. If `is_length_prefixed` is True, assumes length prefix, otherwise fixed size."""
    if is_length_prefixed:
        # Decode length-prefixed BigUint
        length = struct.unpack_from(">I", data, offset)[0]  # Length-prefixed
        offset += 4
        biguint = int.from_bytes(data[offset:offset + length], byteorder="big")
        offset += length
    else:
        # Decode fixed-size BigUint (assuming 4 bytes for royalties)
        biguint = struct.unpack_from(">I", data, offset)[0]
        offset += 4
    return biguint, offset

def decode_string(data, offset):
    """Decode a length-prefixed string."""
    length = struct.unpack_from(">I", data, offset)[0]
    offset += 4
    string = data[offset:offset + length].decode("utf-8")
    offset += length
    return string, offset

def decode_buffer(data, offset):
    """Decode a binary buffer."""
    length = struct.unpack_from(">I", data, offset)[0]
    offset += 4
    buffer = data[offset:offset + length]
    offset += length
    return buffer, offset

def decode_uris(data, offset):
    """Decode a vector of URIs."""
    count = struct.unpack_from(">I", data, offset)[0]
    offset += 4
    uris = []
    for _ in range(count):
        uri, offset = decode_string(data, offset)
        uris.append(uri)
    return uris, offset

def decode_esdt_token_data(binary_data):
    offset = 0

    # Token Type
    token_type = struct.unpack_from(">B", binary_data, offset)[0]
    offset += 1
    print(f"Token Type: {token_type}")

    # Amount (BigUint)
    amount, offset = decode_biguint(binary_data, offset)
    print(f"Amount: {amount}")

    # Frozen (Boolean)
    frozen = struct.unpack_from(">B", binary_data, offset)[0]
    offset += 1
    print(f"Frozen: {bool(frozen)}")

    # Hash
    hash_value, offset = decode_buffer(binary_data, offset)
    print(f"Hash: {hash_value.hex()}")

    # Name
    name, offset = decode_string(binary_data, offset)
    print(f"Name: {name}")

    # Attributes
    attributes, offset = decode_buffer(binary_data, offset)
    print(f"Attributes: {attributes}")

    # Creator
    creator, offset = decode_buffer(binary_data, offset)
    print(f"Creator: {creator.hex()}")

    # Royalties (BigUint)
    royalties, offset = decode_biguint(binary_data, offset, is_length_prefixed=False)
    print(f"Royalties: {royalties}")

    # URIs
    uris, offset = decode_uris(binary_data, offset)
    print(f"URIs: {uris}")

# Example binary data (replace with your actual data)
binary_data1 = b'\x01\x00\x00\x00\x01\x01\x00\x00\x00\x00@709e80c88487a2411e1ee4dfb9f22a861492d20c4765150c0c794abd70f8147c\x00\x00\x00\x13alexandra.udrescu01\x00\x00\x00\x03\x00\x00\x00\x97\xa38\xb0\xe2\r\x83\x84Tf \xac\xf0\x11\xa9\xe1R\x9d\xeb\xb2\xc4\xeb5\xaf\xbb\xac\xc8\xc5&Af\xf1\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x13http://puiemoli.wtf' 
binary_data2 = b"\x01\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x0ebogdan.rizescu\x00\x00\x00\x03\x00\x00\x01d\xc8z\xfd$\xc9\xce\xc6\x08\x04'\xe7\xf3Y\xd8\xc8\x87\xb4(\xc9\x9d\x8e\x8fh\x9a\xdc\xc5\xcb\xf7k\xca\xa8\x00\x00\x00\x01\n\x00\x00\x00\x01\x00\x00\x00\x84https://en.wikipedia.org/wiki/Capybara#/media/File:Hydrochoeris_hydrochaeris_in_Brazil_in_Petr\xc3\xb3polis,_Rio_de_Janeiro,_Brazil_09.jpg"

# Parse the data
parsed_data1 = decode_esdt_token_data(binary_data1)
parsed_data2 = decode_esdt_token_data(binary_data2)
print(parsed_data1)
print('\n', parsed_data2)
