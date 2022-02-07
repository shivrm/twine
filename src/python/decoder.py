from typing import Callable

class DecodeError(Exception):
    pass

def handle_bool(subtype, twine_stream):
    # bool data is stored in the subtype itself and can be determined
    # without reading from the twine stream
    if subtype == 0x00:
        return False

    elif subtype == 0x01:
        return True

    elif subtype == 0x03:
        return None

    else:
        error_msg = f"Unknown bool subtype: {hex(subtype)}"
        raise DecodeError(error_msg)

def handle_int(subtype, twine_stream):
    
    # Specifies whether the integer is signed - stored in highest bit
    is_signed = bool(subtype & 0x08)
    
    # Calculate the number of bytes. Last 3 bits of subtype are calculated
    # using log(byte_count, 2) - 1. We can reverse this to obtain the byte
    # count from the last 2 digits.
    byte_count = 2 ** (subtype & 0x07 - 1)
    
    # Get data from twine stream into a bytearray
    data_bytes = bytearray()
    for _ in range(byte_count):
        next_byte = next(twine_stream)
        data_bytes.append(next_byte)
        
    # Construct an int from the bytearray
    decoded_int = int.from_bytes(data_bytes, "big", signed=is_signed)
    
    return decoded_int

def handle_float(subtype, twine_stream):
    pass

def handle_str(subtype, twine_stream):
    pass

def handle_list(subtype, twine_stream):
    pass

handlers: dict[int, Callable] = {
    0x10: handle_bool,
    0x20: handle_int,
    0x30: handle_float,
    0x40: handle_str,
    0x50: handle_list
}

def decode(twine: bytearray):
    twine_stream = iter(twine)
    
    # Get the data type and subtype
    type_byte = next(twine_stream)
    data_type, subtype = type_byte & 0xf0, type_byte & 0x0f
    
    # Verify that a handler exists for the data
    if data_type not in handlers:
        error_msg = f"type {hex(data_type)} has no handler"
        raise DecodeError(error_msg)
    
    handler = handlers.get(data_type)
    decoded = handler(subtype, twine_stream)
    
    return decoded