from struct import unpack as struct_unpack

from typing import Any, BinaryIO, Callable, Iterator, Union


def _file_to_stream(file: BinaryIO, chunk_size=512):
    while True:
        # Read while not EOF

        data = file.read(chunk_size)

        if not data:
            # EOF
            break

        # Yield each byte
        yield from data


class DecodeError(Exception):
    pass


def _handle_bool(subtype: int, twine_stream: Iterator) -> Union[bool, None]:
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


def _handle_int(subtype: int, twine_stream: Iterator) -> int:

    # Specifies whether the integer is signed - stored in highest bit
    is_signed = bool(subtype & 0x08)

    # Calculate the number of bytes. Last 3 bits of subtype are calculated
    # using log(byte_count, 2) - 1. We can reverse this to obtain the byte
    # count from the last 2 digits.
    byte_count: int = 2 ** ((subtype & 0x07) - 1)

    # Get data from twine stream into a bytearray
    data_bytes = bytearray()
    for _ in range(byte_count):
        next_byte = next(twine_stream)
        data_bytes.append(next_byte)

    # Construct an int from the bytearray
    decoded_int = int.from_bytes(data_bytes, "big", signed=is_signed)

    return decoded_int


def _handle_float(subtype: int, twine_stream: Iterator) -> float:
    # Handle NaN and infinities
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
        unpack_type = "!f"
        byte_count = 4

    # Double precision
    elif precision == 0x02:
        unpack_type = "!d"
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


def _get_single_utf8_char(twine_stream: Iterator) -> str:

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


def _handle_str(subtype: int, twine_stream: Iterator) -> str:
    decoded_str = ""  # Chars will be added to this str after decoding
    # Get length, encoded as an int, from the twine
    length = _handle_any(twine_stream)

    # Decode each char and append it to the str
    for _ in range(length):
        decoded_char = _get_single_utf8_char(twine_stream)
        decoded_str += decoded_char

    return decoded_str


def _handle_list(subtype, twine_stream):
    decoded_list = []  # Elements will be added to this list after decoding
    # Get length, encoded as an int, from the twine
    length = _handle_any(twine_stream)

    # Decode each element of the list and append it to the list
    for _ in range(length):
        decoded_element = _handle_any(twine_stream)
        decoded_list.append(decoded_element)

    return decoded_list


_decoders: dict[int, Callable] = {
    0x10: _handle_bool,
    0x20: _handle_int,
    0x30: _handle_float,
    0x40: _handle_str,
    0x50: _handle_list,
}


def set_decoder(type_code: int, decoder: Callable) -> None:
    _decoders[type_code] = decoder


def _handle_any(twine_stream) -> Any:
    # Get the data type and subtype
    type_byte = next(twine_stream)
    data_type, subtype = type_byte & 0xF0, type_byte & 0x0F

    # Verify that a handler exists for the data
    if data_type not in _decoders:
        error_msg = f"type {hex(data_type)} has no decoder"
        raise DecodeError(error_msg)

    decoder = _decoders.get(data_type)
    decoded = decoder(subtype, twine_stream)

    return decoded


def load(file: BinaryIO, chunk_size=512) -> Any:
    """Loads twine data from a file object

    Args:
        file (BinaryIO): A file opened in 'rb' mode
        chunk_size (int, optional): File will be read in
        chunks of this size. Defaults to 512.

    Returns:
        any: The decoded data
    """
    # Convert file to stream
    stream = _file_to_stream(file, chunk_size=chunk_size)

    # Decode the data and return it
    decoded = _handle_any(stream)
    return decoded


def loads(data: bytes) -> Any:
    """Loads twine data from a bytearray

    Args:
        data (bytes): Twine data as a bytes or bytearray

    Returns:
        any: The decoded data
    """
    # Convert data to stream (iterator)
    stream = iter(data)

    # Decode the data and return it
    decoded = _handle_any(stream)
    return decoded
