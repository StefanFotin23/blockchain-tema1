def decode_biguint(data, offset):
    """
    Decodes a BigUint field.
    """
    length = int.from_bytes(data[offset:offset + 4], byteorder="big")
    offset += 4
    value = int.from_bytes(data[offset:offset + length], byteorder="big")
    offset += length
    return value, offset


def decode_managed_buffer(data, offset):
    """
    Decodes a ManagedBuffer field.
    """
    length = int.from_bytes(data[offset:offset + 4], byteorder="big")
    offset += 4
    buffer_data = data[offset:offset + length]
    offset += length
    return buffer_data.decode('utf-8', errors='ignore'), offset


def decode_esdt_token_data(data):
    """
    Decodes the EsdtTokenData structure.
    """
    offset = 0

    # Decode token_type (1 byte)
    token_type = data[offset]
    offset += 1

    # Decode amount (BigUint)
    amount, offset = decode_biguint(data, offset)

    # Decode frozen (1 byte)
    frozen = bool(data[offset])
    offset += 1

    # Decode hash (ManagedBuffer)
    token_hash, offset = decode_managed_buffer(data, offset)

    # Decode name (ManagedBuffer)
    name, offset = decode_managed_buffer(data, offset)

    # Decode attributes (ManagedBuffer)
    attributes, offset = decode_managed_buffer(data, offset)

    # Decode creator (32 bytes)
    creator = data[offset:offset + 32]
    offset += 32

    # Decode royalties (BigUint)
    royalties, offset = decode_biguint(data, offset)

    # Decode uris (ManagedVec<ManagedBuffer>)
    uri_count = int.from_bytes(data[offset:offset + 4], byteorder="big")
    offset += 4
    uris = []
    for _ in range(uri_count):
        uri, offset = decode_managed_buffer(data, offset)
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

# Example binary data (as received from the Rust smart contract)
binary_data = b'\x01\x00\x00\x00\x01\x01\x00\x00\x00\x00@709e80c88487a2411e1ee4dfb9f22a861492d20c4765150c0c794abd70f8147c\x00\x00\x00\x13alexandra.udrescu01\x00\x00\x00\x03\x00\x00\x00\x97\xa38\xb0\xe2\r\x83\x84Tf \xac\xf0\x11\xa9\xe1R\x9d\xeb\xb2\xc4\xeb5\xaf\xbb\xac\xc8\xc5&Af\xf1\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x13http://puiemoli.wtf'
# Parse the binary data
parsed_data = decode_esdt_token_data(binary_data)
print(parsed_data)