# Twine Data Types

## `bool`
Contains a `true`, `false`, or `null` value.

Type: `0001` or `0x1`

### Subtypes:

|Subtype name  |Binary |Hex   |
|--------------|-------|------|
|`false`       |`0000` |`0x00`|
|`true`        |`0001` |`0x01`|
|`null`        |`0011` |`0x03`|

---

## `int`

Contains a signed or unsigned integer, stored in 8, 16, 32, 64 or 128 bits.

Type: `0010` or `0x2`


### Subtypes:

|Subtype name     |Binary |Hex   |
|-----------------|-------|------|
|`unsigned int8`  |`0001` |`0x01`|
|`unsigned int16` |`0010` |`0x02`|
|`unsigned int32` |`0011` |`0x03`|
|`unsigned int64` |`0100` |`0x04`|
|`unsigned int128`|`0101` |`0x05`|
|`signed int8`    |`1001` |`0x09`|
|`signed int16`   |`1010` |`0x0a`|
|`signed int32`   |`1011` |`0x0b`|
|`signed int64`   |`1100` |`0x0c`|
|`signed int128`  |`1101` |`0x0d`|

---

## `float`

Contains a floating point value, can be single-precision, double-precision, or quadruple-precision float.

Type: `0011` or `0x3`

### Subtypes:

|Subtype name  |Binary |Hex   |
|--------------|-------|------|
|`binary32`    |`0001` |`0x01`|
|`binary64`    |`0010` |`0x02`|
|`binary128`   |`0011` |`0x03`|
|`NaN`         |`0000` |`0x00`|
|`+Infinity`   |`0100` |`0x04`|
|`-Infinity`   |`1100` |`0x0c`|

---

## `str`

Contains a string of UTF-8 characters.

Type: `0100` or `0x4`

### Arguments
- `length` (`int`): The length of the string

---

## `list`

Contains a list of data structures

Type: `0101` or `0x5`

### Arguments
- `length` (`int`): The length of the list

