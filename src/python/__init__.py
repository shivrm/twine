from typing import Callable

from .decoder import load, loadb, set_decoder
from .encoder import dump, dumpb, set_encoder


def set_handler(
    data_type: type, type_code: int, encoder: Callable, decoder: Callable
) -> None:
    """Set the handlers for a data type

    Args:
        data_type (type): The type of the data, used when encoding
        type_code (int): Code used to identify type when decoding
        encoder (Callable): Function to call when encoding data
        decoder (Callable): Function to call when decoding data
    """
    set_encoder(data_type, encoder)
    set_decoder(data_type, decoder)
