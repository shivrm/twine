from struct import unpack as struct_unpack

from typing import Callable, Iterator, Union


class DecodeError(Exception):
    pass


def handle_bool(subtype: int, twine_stream: Iterator) -> Union[bool, None]:
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


def handle_int(subtype: int, twine_stream: Iterator) -> int:

    # Specifies whether the integer is signed - stored in highest bit
    is_signed = bool(subtype & 0x08)

    # Calculate the number of bytes. Last 3 bits of subtype are calculated
    # using log(byte_count, 2) - 1. We can reverse this to obtain the byte
    # count from the last 2 digits.
    byte_count: int = 2 ** (subtype & 0x07 - 1)

    # Get data from twine stream into a bytearray
    data_bytes = bytearray()
    for _ in range(byte_count):
        next_byte = next(twine_stream)
        data_bytes.append(next_byte)

    # Construct an int from the bytearray
    decoded_int = int.from_bytes(data_bytes, "big", signed=is_signed)

    return decoded_int


def handle_float(subtype: int, twine_stream: Iterator) -> float:
    # Handle NaN and infinities
    print(subtype)
    if subtype == 0x0:
        return float("nan")

    elif subtype == 0x4:
        return float("inf")

    elif subtype == 0xB:
        return float("-inf")

    # Float precision type is encoded in last 2 bytes of subtype
    precision = subtype & 0x03

    # Single precision
    if precision == 0x01:
        unpack_type = "f"
        byte_count = 4

    # Double precision
    elif precision == 0x02:
        unpack_type = "d"
        byte_count = 8

    # NOTE: Quadruple precision support has not been added yet
    else:
        error_msg = f"Unknown float subtype: {hex(subtype)}"
        raise DecodeError(error_msg)

    # Get data from twine stream into a bytearray
    data_bytes = bytearray()
    for _ in range(byte_count):
        next_byte = next(twine_stream)
        data_bytes.append(next_byte)

    # Construct float of correct precision from data_bytes
    decoded_float = struct_unpack(unpack_type, data_bytes)[0]

    return decoded_float


def get_single_utf8_char(twine_stream: Iterator) -> str:

    # Get first byte of character.
    first_byte = next(twine_stream)

    # Determine how long the character is using the first byte
    if first_byte & 0xF0 == 0xF0:
        bytes_to_read = 3

    elif first_byte & 0xE0 == 0xE0:
        bytes_to_read = 2

    elif first_byte & 0xC0 == 0xE0:
        bytes_to_read = 1

    elif not first_byte & 0x80:
        bytes_to_read = 0
    else:
        error_msg = "invalid UTF-8 sequence"
        raise DecodeError(error_msg)

    # Read bytes from the stream into a bytearray
    data_bytes = bytearray([first_byte])
    for _ in range(bytes_to_read):
        byte_read = next(twine_stream)
        data_bytes.append(byte_read)

    # Decode bytes to str and return
    return bytes(data_bytes).decode("utf8")


def handle_str(subtype: int, twine_stream: Iterator) -> str:
    decoded_str = ""  # Chars will be added to this str after decoding
    # Get length, encoded as an int, from the twine
    length = decode(twine_stream)

    # Decode each char and append it to the str
    for _ in range(length):
        decoded_char = get_single_utf8_char(twine_stream)
        decoded_str += decoded_char

    return decoded_str


def handle_list(subtype, twine_stream):
    decoded_list = []  # Elements will be added to this list after decoding
    # Get length, encoded as an int, from the twine
    length = decode(twine_stream)

    # Decode each element of the list and append it to the list
    for _ in range(length):
        decoded_element = decode(twine_stream)
        decoded_list.append(decoded_element)

    return decoded_list


handlers: dict[int, Callable] = {
    0x10: handle_bool,
    0x20: handle_int,
    0x30: handle_float,
    0x40: handle_str,
    0x50: handle_list,
}


def set_handler(data_type: type, handler: Callable) -> None:
    type_name = data_type.__name__
    handlers[type_name] = handler


def decode(twine: bytearray):
    twine_stream = iter(twine)

    # Get the data type and subtype
    type_byte = next(twine_stream)
    data_type, subtype = type_byte & 0xF0, type_byte & 0x0F

    # Verify that a handler exists for the data
    if data_type not in handlers:
        error_msg = f"type {hex(data_type)} has no handler"
        raise DecodeError(error_msg)

    handler = handlers.get(data_type)
    decoded = handler(subtype, twine_stream)

    return decoded
