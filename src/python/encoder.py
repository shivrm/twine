class EncodeError(Exception):
    pass

def handle_none(data: None) -> bytearray:
    pass

def handle_bool(data: bool) -> bytearray:
    pass

def handle_int(data: int) -> bytearray:
    pass

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