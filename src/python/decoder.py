from typing import Callable

class DecodeError(Exception):
    pass

def handle_bool(subtype, twine_stream):
    pass

def handle_int(subtype, twine_stream):
    pass

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