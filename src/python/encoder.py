from math import log, ceil
from struct import pack as struct_pack, unpack as struct_unpack

from typing import Callable


def _ceil_divide(dividend: float, divisor: int) -> int:
    # https://stackoverflow.com/a/17511341/16990573
    return -(dividend // -divisor)


class EncodeError(Exception):
    pass


def handle_none(data: None) -> bytearray:
    yield 0x13


def handle_bool(data: bool) -> bytearray:
    # Return 0x10 if data is False, 0x11 if it is True.
    yield 0x10 + data


def handle_int(data: int) -> bytearray:

    # Check for zero as it does not work with log
    if data == 0:
        yield from [0x21, 0x00]
        return

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
    actual_byte_count: int = 2 ** ceil(log(min_byte_count, 2))

    # Raise error if int requires more than 16 bytes (128 bits)
    # NOTE: If BigInt support is added, this should be updated
    if actual_byte_count > 16:
        error_msg = f"int {data} can not be stored in 128 bits"
        raise EncodeError(error_msg)

    # Calculate data structure type byte from `is_negative` and the
    # number of bytes. 0x20 specifies the int type.
    signed_flag = is_negative << 3
    int_type_index = int(log(actual_byte_count, 2) + 1)
    type_byte = 0x20 + signed_flag + int_type_index

    yield type_byte

    # Convert the data to a bytes object, then yield it
    yield from data.to_bytes(actual_byte_count, byteorder="big", signed=is_negative)


def handle_float(data: float) -> bytearray:
    # Check for NaN (NaN != NaN) and both infinities
    if data != data:
        yield 0x30
        return

    elif data == float("inf"):
        yield 0x34
        return

    elif data == float("-inf"):
        yield 0x3b
        return

    # Convert to single precision float
    single_precision_bytes: bytes = struct_pack("f", data)
    single_precision_value: float = struct_unpack("f", single_precision_bytes)[0]

    # If single-precision float does not have any loss of precision, then
    # store as a single-precision float. If there is loss of precision,
    # then store as double-precision float.
    if data == single_precision_value:
        # Yield type byte, and then the bytes for the single-precision float
        yield 0x31
        yield from single_precision_bytes
        
    else:
        # Yield type byte, and then the bytes for the double-precision float
        yield 0x32
        yield from struct_pack("d", data)


def handle_str(data: str) -> bytearray:
    yield 0x40 # Yield type byte
    yield from handle_int(len(data)) # Yield length bytes
    yield from data.encode("utf8") # Yield char data


def handle_list(data: list) -> bytearray:

    yield 0x50 # Yield type byte
    yield from handle_int(len(data)) # Yield length bytes

    # Yield each element after encoding it
    for element in data:
        yield from encode(element)

handlers: dict[str, Callable] = {
    "NoneType": handle_none,
    "bool": handle_bool,
    "int": handle_int,
    "float": handle_float,
    "str": handle_str,
    "list": handle_list,
}

def set_handler(data_type: type, handler: Callable) -> None:
    type_name = data_type.__name__
    handlers[type_name] = handler


def encode(data):
    type_name: str = type(data).__name__

    # Verify that a handler exists for the data
    if type_name not in handlers:
        error_msg = f"type {type_name!r} has no handler"
        raise EncodeError(error_msg)

    handler: Callable = handlers.get(type_name)
    encoded: bytearray = handler(data)

    yield from encoded