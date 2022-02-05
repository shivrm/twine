from math import log, ceil

def _ceil_divide(dividend: float, divisor: int) -> int:
    # https://stackoverflow.com/a/17511341/16990573
    return -(dividend // -divisor)

class EncodeError(Exception):
    pass

def handle_none(data: None) -> bytearray:
    return bytearray([0x13])

def handle_bool(data: bool) -> bytearray:
    # Return 0x10 if data is False, 0x11 if it is True.
    return bytearray([0x10 + data])

def handle_int(data: int) -> bytearray:
    
    # Check for zero as it does not work with log
    if data == 0:
        return bytearray([0x21, 0x00])
    
    is_negative = data < 0
    
    # Use 2s complement to get a positive integer with equal magnitude
    # https://stackoverflow.com/a/48436436/16990573
    unsigned_data = ~data if is_negative else data
    bit_count = unsigned_data.bit_length() + is_negative
    
    # Calculate the minimum number of bytes required to store the int
    # then round up to the nearest power of 2 to get actual byte count
    #
    # https://stackoverflow.com/a/466256/16990573
    min_byte_count = _ceil_divide(bit_count, 8)
    actual_byte_count = 2 ** ceil(log(min_byte_count, 2))
    
    # Raise error if int requires more than 16 bytes (128 bits)
    # NOTE: If BigInt support is added, this should be updated
    if actual_byte_count > 16:
        error_msg = f"int {data} can not be stored in 128 bits"
        raise EncodeError(error_msg)
    
    # Calculate data structure type byte from `is_negative` and the
    # number of bytes. 0x20 specifies the int type.
    signed_flag = is_negative << 3
    int_type_index = int(log(actual_byte_count*2, 2))
    type_byte = 0x20 + signed_flag + int_type_index
    
    # Convert the data to a bytes object, unsigned unless it's negative
    data_bytes = data.to_bytes(actual_byte_count, byteorder="big", signed=is_negative)

    # Return a bytearray containing the type byte and the data
    return bytearray([type_byte, *data_bytes])

def handle_float(data: float) -> bytearray:
    pass

def handle_str(data: str) -> bytearray:
    pass

def handle_list(data: list) -> bytearray:
    pass

handlers: dict[str, function] = {
    'NoneType': handle_none,
    'bool': handle_bool,
    'int': handle_int,
    'float': handle_float,
    'str': handle_str,
    'list': handle_list
}

def encode(data) -> bytearray:
    type_name: str = type(data).__name__

    # Verify that a handler exists for the data
    if type_name not in handlers:
        error_msg = f"type {type_name!r} has no handler"
        raise EncodeError(error_msg)
    
    handler = handlers.get(type_name)
    encoded: bytearray = handler(data)
    
    return encoded