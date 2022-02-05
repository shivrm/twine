# twine

`twine` is a simple format for serializing data. Twine is still in development and breaking changes may occur. Use with caution.

⚠️ Much of this documentation could change as development continues.

A file containing such data is called a *twine*, and 
should have the `.twine` file extension.

# Structure

a twine contains only data, no header. ⚠️ A header may be added in future to store custom data types.

Data in a twine is stored as data structures. Data structures are of multiple types to hold different types of data.

Similar to a JSON file, a twine is one big data structure. If this is an `array` or a `map`, it may contain nested data structures.

The first byte of each data structure specifies it's type. The higher 4 bits specify the primary type while the lower 4 bits specify the sub-type.

Each type has a handler, which reads bytes from the file as necessary to parse the information.

## Data Types
twine has 5 built-in data types:
 - `bool`: for storing values such as `true`, `false` and `null`
 - `int`: for storing integers
 - `float`: for storing floating-point values
 - `char`: for storing a single UTF-8 character
 - `array`: for storing a sequence of data structures.
 - ⚠️ a `map` type may be implemented in future to store key-value pairs

## Sub Types

Each data type also has several sub-types:
- `bool` has the `true`, `false`, and `null`	subtypes for storing these singleton values. ❓ should an `undefined` type be added?

 - `int` has the `int8`, `int16`, `int32`, `int64`, `int128` and their `unsigned` versions for storing 8-bit, 16-bit, 32-bit 64-bit and 128-bit unsigned and signed integers.

 - `float32`, `float64`, and `float128` for storing single, double and quadruple precision floats. There are also subtypes for `Infinity`, `-Infinity` and `NaN` ⚠️ Does not distinguish between quiet NaN and signalling NaN

 - `char` does not have any subtypes

 - `array` does not have any subtypes. ⚠️ A `fixed-type array` subtype could be added to specify that all elements in the array are of the same type.

## Values for data types:
- `bool`: `0001 xxxx`:
	- `false`: `0000`,
	- `true`: `0001`
	- `null`: `0011`

- `int`: `0010 xxxx`:
	- `unsigned`: `0xxx`
	- `signed`: `1xxx`
	- `int8`: `x001`
	- `int16`: `x010`
	- `int32`: `x011`
	- `int64`: `x100`
	- `int128`: `x101`

 - `float`: `0011 xxxx`:
	 - `NaN`: `0000`
	 - ⚠️ `sNaN`: `1111`
	 - `float32`: `0001`
	 - `float64`: `0010`
	 - `float128`: `0011`
	 - `+Inf`: `0100`
	 - `-Inf`: `1100`

 - `char`: `0100 xxxx`
	 - subtype: `0000`

 - `array`: `0101 xxxx`
	 - subtype: `0000`

## Examples

```json
JSON: [1, 2, 3, 4, 5]

// twine Syntax Tree
array[5] {
 int(1), int(2), int(3), int(4), int(5)
}

// twine data as hex:
0x50 0x05 0x21 0x01 0x21 0x02
0x21 0x03 0x21 0x04 0x21 0x05

// explanation
0x50 -> array
0x05 -> of length 5

0x21 -> unsigned int8
0x01 -> value 1

0x21 -> unsigned int8
0x02 -> value 2
.
.
.
0x21 -> unsigned int8
0x05 -> value 5
```

# License
twine is licensed under the MIT License.

[LICENSE.md](LICENSE.md)