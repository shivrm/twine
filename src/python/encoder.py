from math import log, ceil
from struct import pack as struct_pack, unpack as struct_unpack

from typing import Union, Generator, Callable, BinaryIO


def _ceil_divide(dividend: float, divisor: int) -> int:
    # https://stackoverflow.com/a/17511341/16990573
    return -(dividend // -divisor)


def _iter_to_byte_chunks(iterable, chunk_size=512) -> Generator:
    # Items in current chunk, and number of items in current chunk
    chunk_content = bytearray()
    content_size = 0

    # Iterate over the iterable and add each to the chunk
    for item in iterable:
        chunk_content.append(item)
        content_size += 1

        # If the chunk contains as many elements as the chunk size,
        # then yield the chunk, and begin a new chunk
        if content_size == chunk_size:
            yield chunk_content

            chunk_content = bytearray()
            content_size = 0

    # If there are any remaining elements, yield them as well
    if content_size:
        yield chunk_content


class EncodeError(Exception):
    pass


def _handle_none(data: None) -> Generator:
    yield 0x13


def _handle_bool(data: bool) -> Generator:
    # Return 0x10 if data is False, 0x11 if it is True.
    yield 0x10 + data


def _handle_int(data: int) -> Generator:

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


def _handle_float(data: float) -> Generator:
    # Check for NaN (NaN != NaN) and both infinities
    if data != data:
        yield 0x30
        return

    elif data == float("inf"):
        yield 0x34
        return

    elif data == float("-inf"):
        yield 0x3B
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


def _handle_str(data: str) -> Generator:
    yield 0x40  # Yield type byte
    yield from _handle_int(len(data))  # Yield length bytes
    yield from data.encode("utf8")  # Yield char data


def _handle_list(data: list) -> Generator:

    yield 0x50  # Yield type byte
    yield from _handle_int(len(data))  # Yield length bytes

    # Yield each element after encoding it
    for element in data:
        yield from _handle_any(element)


_encoders: dict[str, Callable] = {
    "NoneType": _handle_none,
    "bool": _handle_bool,
    "int": _handle_int,
    "float": _handle_float,
    "str": _handle_str,
    "list": _handle_list,
}


def set_encoder(data_type: type, encoder: Callable) -> None:
    type_name = data_type.__name__
    _encoders[type_name] = encoder


def _handle_any(data) -> Generator:
    type_name: str = type(data).__name__

    # Verify that a handler exists for the data
    if type_name not in _encoders:
        error_msg = f"type {type_name!r} has no encoder"
        raise EncodeError(error_msg)

    encoder: Callable = _encoders.get(type_name)
    encoded: bytearray = encoder(data)

    yield from encoded


def dump(data, file: BinaryIO, chunk_size: int = 512) -> None:
    """Encode data and write to a file

    Args:
        data (any): The data to encode
        file (BinaryIO): A file opened in wb mode
        chunk_size (int, optional): Size of each chunk written to the
        file. Defaults to 512.
    """
    # Encode the data
    encoded = _handle_any(data)

    # Write to file in chunks
    for chunk in _iter_to_byte_chunks(encoded, chunk_size):
        file.write(chunk)


def dumpb(data, lazy=False) -> Union[bytes, Generator]:
    """Encodes data and return as a bytearray

    Args:
        data (any): The data to encode
        lazy (bool, optional): Whether encoded data should be returned
        as a generator. Defaults to False.

    Returns:
        Union[bytes, generator]: A generator or bytes object containing
        the encoded data.
    """
    # Encode the data
    encoded = _handle_any(data)

    # Return as generator if lazy, else convert it into a bytes object
    if lazy:
        return encoded
    else:
        return bytes(encoded)
