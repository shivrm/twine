# Python Implementation 

## function `load`

Loads twine data from a file object.

```py
def load(file: BinaryIO, chunk_size=512) -> any:
```

### Arguments
 - `file` (`BinaryIO`): A file opened in 'rb' mode
 - `chunk_size` (`int`, optional): File will be read in
 chunks of this size. Defaults to 512.

### Returns
 - `any`: The decoded data

---

## function `loads`

Loads twine data from a bytes-like object

```py
def load(data: ByteString) -> any:
```

### Argsuments
 - `data` (`ByteString`): A bytes-like object containing the twine data.

### Returns
 - `any`: The decoded data

---

## function `dump`

Encodes data and writes the result to a file

```py
def dump(data, file: BinaryIO, chunk_size: int = 512) -> None:
```

### Arguments
 - `data` (`any`): The data to encode
 - `file` (`BinaryIO`): A file opened in wb mode
 - `chunk_size` (`int`, optional): Size of each chunk written to the file. Defaults to `512`.

---

## function `dumps`

Encodes data and returns it either as a `bytes` object or as a `generator`.

```py
def dumpb(data, lazy: bool = False) -> Union[bytes, Generator]
```

### Arguments
 - `data` (`any`): The data to encode
 - `lazy` (`bool`, optional): Whether encoded data should be returned as a `generator`. Defaults to `False`.

### Returns
 - `Union[bytes, Generator]`: A generator, or bytes object containing the encoded data

---

## function `set_handlers`

Set the handlers for a data type

```py
def set_handlers(data_type: type, type_code: int, encoder: Callable, decoder: Callable) -> None:
```
### Arguments
 - `data_type` (`type`): The type of the data, used when encoding
 - `type_code` (`int`): Code used to identify type when decoding
 - `encoder` (`Callable`): Function to call when encoding data
 - `decoder` (`Callable`): Function to call when decoding data